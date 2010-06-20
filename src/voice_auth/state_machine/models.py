from django.db import models
from django.db import transaction
from django.conf import settings
import logging

from misc.db import set_isolation_level

class IllegalStateError(Exception): pass

class StateMachine(models.Model):
    class Meta:
        abstract = True

    initial_state = 'created'

    dbms_support_serializible = not settings.DATABASE_ENGINE.endswith('sqlite3') 

    def weak_transition(self, to_state,
            state_history_attr=None, **state_transition_kwargs):
        from_state = self.state_id

        if self.transition_is_allowed(from_state, to_state):
            self.state_id = to_state
            self.save()

            if state_history_attr is not None:
                getattr(self, state_history_attr).create(from_state_id=from_state,
                    to_state_id=to_state, **state_transition_kwargs)

            logging.info('%s "%s" about to switch to state "%s"' % (self.__class__.__name__, self.id, to_state))
        else:
            raise IllegalStateError(self.__class__.__name__, self.id, self.state_id)

    @transaction.commit_manually
    def transition(self, to_state, state_history_attr=None,
            **state_transition_kwargs):
        try:
            if self.dbms_support_serializible:
                set_isolation_level('SERIALIZABLE')
            locked_self = self.__class__.objects.get(id=self.id) # current locked instance
            from_state = locked_self.state_id

            if self.transition_is_allowed(from_state, to_state):
                self.state_id = to_state
                self.save()

                if state_history_attr is not None:
                    getattr(self, state_history_attr).create(from_state_id=from_state,
                        to_state_id=to_state, **state_transition_kwargs)
            else:
                raise IllegalStateError(self.__class__.__name__, self.id, self.state_id)
        except:
            transaction.rollback()
            raise
        else:
            transaction.commit()
            logging.info('%s "%s" switched to state "%s"' % (locked_self.__class__.__name__, locked_self.id, to_state))

    def transition_is_allowed(self, from_state, to_state):
        allowed_states = self.transition_table.get(from_state)
        return allowed_states and to_state in allowed_states

    def save(self, *args, **kwargs):
        if not self.state_id:
            self.state_id = self.initial_state
        return super(StateMachine, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"%s" % (self.state_id)

