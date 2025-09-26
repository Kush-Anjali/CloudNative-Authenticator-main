import structlog

# Custom processor to rename the 'level' field to 'severity'
def rename_level_to_severity(logger, method_name, event_dict):
    if 'level' in event_dict:
        event_dict['severity'] = event_dict.pop('level')
    return event_dict

# Configure structlog
def configure_structlog():
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            rename_level_to_severity,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.ExceptionPrettyPrinter(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
