const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const rateLimit = require('express-rate-limit');
const morgan = require('morgan');
const mongoose = require('mongoose');
const redis = require('redis');
const session = require('express-session');
const RedisStore = require('connect-redis')(session);
const jwt = require('jsonwebtoken');
const cron = require('node-cron');

// Import configurations
const config = require('./config/config');
const logger = require('./config/logger');

// Import middleware
const authMiddleware = require('./middleware/auth');
const errorMiddleware = require('./middleware/error');
const validationMiddleware = require('./middleware/validation');

// Import routes
const authRoutes = require('./routes/auth');
const deviceRoutes = require('./routes/devices');
const securityRoutes = require('./routes/security');
const energyRoutes = require('./routes/energy');
const analyticsRoutes = require('./routes/analytics');
const settingsRoutes = require('./routes/settings');
const webhookRoutes = require('./routes/webhooks');

// Import services
const MQTTService = require('./services/mqttService');
const WebSocketService = require('./services/websocketService');
const DatabaseService = require('./services/databaseService');
const AIService = require('./services/aiService');
const SecurityService = require('./services/securityService');
const EnergyService = require('./services/energyService');
const NotificationService = require('./services/notificationService');
const SchedulerService = require('./services/schedulerService');

// Import utilities
const swaggerSetup = require('./utils/swagger');

class SmartHomeServer {
    constructor() {
        this.app = express();
        this.server = http.createServer(this.app);
        this.io = socketIo(this.server, {
            cors: {
                origin: config.cors.origin,
                methods: ["GET", "POST"],
                credentials: true
            }
        });
        
        this.redisClient = null;
        this.mqttService = null;
        this.wsService = null;
        this.aiService = null;
        this.securityService = null;
        this.energyService = null;
        this.notificationService = null;
        this.schedulerService = null;
    }

    async initialize() {
        try {
            // Initialize database
            await this.initializeDatabase();
            
            // Initialize Redis
            await this.initializeRedis();
            
            // Setup middleware
            this.setupMiddleware();
            
            // Setup routes
            this.setupRoutes();
            
            // Initialize services
            await this.initializeServices();
            
            // Setup error handling
            this.setupErrorHandling();
            
            // Setup scheduled tasks
            this.setupScheduledTasks();
            
            logger.info('Smart Home Server initialized successfully');
        } catch (error) {
            logger.error('Failed to initialize server:', error);
            process.exit(1);
        }
    }

    async initializeDatabase() {
        try {
            await mongoose.connect(config.database.mongodb.uri, {
                useNewUrlParser: true,
                useUnifiedTopology: true,
            });
            logger.info('Connected to MongoDB');
        } catch (error) {
            logger.error('MongoDB connection error:', error);
            throw error;
        }
    }

    async initializeRedis() {
        try {
            this.redisClient = redis.createClient({
                host: config.database.redis.host,
                port: config.database.redis.port,
                password: config.database.redis.password,
            });
            
            await this.redisClient.connect();
            logger.info('Connected to Redis');
        } catch (error) {
            logger.error('Redis connection error:', error);
            throw error;
        }
    }

    setupMiddleware() {
        // Security middleware
        this.app.use(helmet({
            contentSecurityPolicy: {
                directives: {
                    defaultSrc: ["'self'"],
                    styleSrc: ["'self'", "'unsafe-inline'"],
                    scriptSrc: ["'self'"],
                    imgSrc: ["'self'", "data:", "https:"],
                },
            },
        }));

        // CORS middleware
        this.app.use(cors({
            origin: config.cors.origin,
            credentials: true,
            methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
            allowedHeaders: ['Content-Type', 'Authorization'],
        }));

        // Compression middleware
        this.app.use(compression());

        // Rate limiting
        const limiter = rateLimit({
            windowMs: 15 * 60 * 1000, // 15 minutes
            max: 100, // Limit each IP to 100 requests per windowMs
            message: 'Too many requests from this IP, please try again later.',
        });
        this.app.use('/api/', limiter);

        // Logging middleware
        this.app.use(morgan('combined', {
            stream: { write: message => logger.info(message.trim()) }
        }));

        // Body parsing middleware
        this.app.use(express.json({ limit: '10mb' }));
        this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));

        // Session middleware
        this.app.use(session({
            store: new RedisStore({ client: this.redisClient }),
            secret: config.session.secret,
            resave: false,
            saveUninitialized: false,
            cookie: {
                secure: config.env === 'production',
                httpOnly: true,
                maxAge: 24 * 60 * 60 * 1000, // 24 hours
            },
        }));

        // Health check endpoint
        this.app.get('/health', (req, res) => {
            res.status(200).json({
                status: 'OK',
                timestamp: new Date().toISOString(),
                uptime: process.uptime(),
                memory: process.memoryUsage(),
            });
        });
    }

    setupRoutes() {
        // API routes
        this.app.use('/api/auth', authRoutes);
        this.app.use('/api/devices', authMiddleware, deviceRoutes);
        this.app.use('/api/security', authMiddleware, securityRoutes);
        this.app.use('/api/energy', authMiddleware, energyRoutes);
        this.app.use('/api/analytics', authMiddleware, analyticsRoutes);
        this.app.use('/api/settings', authMiddleware, settingsRoutes);
        this.app.use('/api/webhooks', webhookRoutes);

        // API documentation
        swaggerSetup(this.app);

        // Serve static files
        this.app.use('/uploads', express.static('uploads'));

        // 404 handler
        this.app.use('*', (req, res) => {
            res.status(404).json({
                error: 'Endpoint not found',
                path: req.originalUrl,
            });
        });
    }

    async initializeServices() {
        try {
            // Initialize MQTT Service
            this.mqttService = new MQTTService(config.mqtt);
            await this.mqttService.connect();

            // Initialize WebSocket Service
            this.wsService = new WebSocketService(this.io, this.redisClient);
            this.wsService.initialize();

            // Initialize AI Service
            this.aiService = new AIService(config.ai);
            await this.aiService.initialize();

            // Initialize Security Service
            this.securityService = new SecurityService(this.mqttService, this.wsService);
            await this.securityService.initialize();

            // Initialize Energy Service
            this.energyService = new EnergyService(this.mqttService, this.redisClient);
            await this.energyService.initialize();

            // Initialize Notification Service
            this.notificationService = new NotificationService(config.notifications);
            await this.notificationService.initialize();

            // Initialize Scheduler Service
            this.schedulerService = new SchedulerService(this.mqttService);
            this.schedulerService.initialize();

            // Setup service event handlers
            this.setupServiceEventHandlers();

            logger.info('All services initialized successfully');
        } catch (error) {
            logger.error('Service initialization error:', error);
            throw error;
        }
    }

    setupServiceEventHandlers() {
        // MQTT message handlers
        this.mqttService.on('deviceUpdate', (data) => {
            this.wsService.broadcast('deviceUpdate', data);
        });

        this.mqttService.on('sensorData', (data) => {
            this.energyService.processSensorData(data);
            this.wsService.broadcast('sensorData', data);
        });

        this.mqttService.on('securityAlert', (alert) => {
            this.securityService.handleAlert(alert);
            this.notificationService.sendAlert(alert);
            this.wsService.broadcast('securityAlert', alert);
        });

        // Security service handlers
        this.securityService.on('intrusionDetected', (event) => {
            this.notificationService.sendEmergencyAlert(event);
            this.wsService.broadcast('emergency', event);
        });

        // Energy service handlers
        this.energyService.on('highUsageAlert', (data) => {
            this.notificationService.sendEnergyAlert(data);
            this.wsService.broadcast('energyAlert', data);
        });

        // WebSocket handlers
        this.wsService.on('userCommand', async (command) => {
            try {
                const response = await this.aiService.processCommand(command);
                this.mqttService.publishCommand(response);
            } catch (error) {
                logger.error('Command processing error:', error);
            }
        });
    }

    setupErrorHandling() {
        // Global error handler
        this.app.use(errorMiddleware);

        // Unhandled promise rejection handler
        process.on('unhandledRejection', (reason, promise) => {
            logger.error('Unhandled Rejection at:', promise, 'reason:', reason);
        });

        // Uncaught exception handler
        process.on('uncaughtException', (error) => {
            logger.error('Uncaught Exception:', error);
            process.exit(1);
        });

        // Graceful shutdown
        process.on('SIGTERM', () => this.gracefulShutdown());
        process.on('SIGINT', () => this.gracefulShutdown());
    }

    setupScheduledTasks() {
        // Energy usage reporting (daily)
        cron.schedule('0 0 * * *', async () => {
            try {
                await this.energyService.generateDailyReport();
                logger.info('Daily energy report generated');
            } catch (error) {
                logger.error('Error generating daily energy report:', error);
            }
        });

        // Security system health check (every hour)
        cron.schedule('0 * * * *', async () => {
            try {
                await this.securityService.performHealthCheck();
                logger.info('Security system health check completed');
            } catch (error) {
                logger.error('Security health check error:', error);
            }
        });

        // System backup (weekly)
        cron.schedule('0 2 * * 0', async () => {
            try {
                await DatabaseService.createBackup();
                logger.info('Weekly backup completed');
            } catch (error) {
                logger.error('Backup error:', error);
            }
        });

        // Cleanup old logs (monthly)
        cron.schedule('0 0 1 * *', async () => {
            try {
                await DatabaseService.cleanupOldLogs();
                logger.info('Old logs cleanup completed');
            } catch (error) {
                logger.error('Log cleanup error:', error);
            }
        });
    }

    async gracefulShutdown() {
        logger.info('Received shutdown signal, starting graceful shutdown...');

        // Close server
        this.server.close(() => {
            logger.info('HTTP server closed');
        });

        // Close database connections
        try {
            await mongoose.connection.close();
            logger.info('MongoDB connection closed');
        } catch (error) {
            logger.error('Error closing MongoDB connection:', error);
        }

        // Close Redis connection
        try {
            await this.redisClient.quit();
            logger.info('Redis connection closed');
        } catch (error) {
            logger.error('Error closing Redis connection:', error);
        }

        // Close MQTT connection
        if (this.mqttService) {
            await this.mqttService.disconnect();
            logger.info('MQTT connection closed');
        }

        process.exit(0);
    }

    start() {
        const port = config.server.port || 3001;
        this.server.listen(port, () => {
            logger.info(`Smart Home Server running on port ${port}`);
            logger.info(`Environment: ${config.env}`);
            logger.info(`API Documentation: http://localhost:${port}/api-docs`);
        });
    }
}

// Create and start server
async function startServer() {
    const server = new SmartHomeServer();
    await server.initialize();
    server.start();
}

// Start the server
if (require.main === module) {
    startServer().catch((error) => {
        logger.error('Failed to start server:', error);
        process.exit(1);
    });
}

module.exports = SmartHomeServer;