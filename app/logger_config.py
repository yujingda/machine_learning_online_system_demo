import logging
import logging.config
import os

def setup_logging(log_dir='logs'):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'detailed': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            }
        },
        'handlers': {
            'file': {
                'class': 'logging.FileHandler',
                'filename': os.path.join(log_dir, 'dataset_module.log'),
                'formatter': 'detailed',
                'level': 'DEBUG',
            }
        },
        'loggers': {
            'dataset_module': {
                'handlers': ['file'],
                'level': 'DEBUG',
            }
        }
    })

logger = logging.getLogger('dataset_module')
