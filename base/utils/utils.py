from django.contrib.auth.tokens import PasswordResetTokenGenerator


#Ok so i've spent a good amount of time reading this code and ill try to explain it
#for future me
#
#A token that is being sent to the user is compromised of 2 parts timestamp
#and hash it looks like this "bsewsm-265fbaff66232e03919aa6cc27197374"
#they are separated by the - so "bsewsm" would be the timestamp and the rest the
#has, we do not change anything that has to do with the timestamp the only thing
#we change is the timout duration with PASSWORD_RESET_TIMEOUT in settings.py
#we also do not change the salting or security all we change is the stuff that
#gets mixed in the eventual hash, basicly what we do here is if any of these
#values change then the hash will not validate

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(timestamp) + str(user.is_verified)

class PasswordTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(timestamp) + str(user.password) + str(user.email)

generate_token = TokenGenerator()
password_reset_token = PasswordTokenGenerator()
