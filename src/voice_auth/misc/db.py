from django.db import connections, DEFAULT_DB_ALIAS, transaction

# ANSI 92 compliant
# level = one of ('READ UNCOMMITTED', 'READ COMMITTED', 'REPEATABLE READ', 'SERIALIZABLE')
def set_isolation_level(level, using=None):
    transaction.rollback() # clear transaction state NOTE this is a little bit hacky :-(
    c = _connection(using).cursor()
    c.execute('SET TRANSACTION ISOLATION LEVEL %s' % level)

# NOTE DB-specific (maybe)
def get_isolation_level(using=None):
    c = _connection(using).cursor()
    c.execute('SHOW TRANSACTION ISOLATION LEVEL')
    return c.fetchone()[0]

# NOTE DB-specific
def lock_table(model, mode='EXCLUSIVE', using=None):
    cursor = _connection(using).cursor()
    cursor.execute('LOCK TABLE %s IN %s MODE' % (model._meta.db_table, mode))

def close_connection(using=None):
    _connection(using).close()

def _connection(using=None):
    if using is None:
        using = DEFAULT_DB_ALIAS
    return connections[using]
