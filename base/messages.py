# Displayed when a user tries to enter a post that they don't have permision to
ERR_POSTVIEW_NOPERM = "You cant access this page '%s'"
# Displayed when a user edits a post successfully
SUC_POSTEDIT_ACCEPT = "Post successfully edited"
# Displayed when a user cannot edit the post
ERR_POSTEDIT_NOPERM = "You may not edit '%s'"
# Displayed when a user reacts to a post successfully
SUC_REACTADDPOST_ACCEPT = "Reaction added successfully"
# Displayed when user can't react to the post
ERR_REACTADDPOST_NOPERM = "You may not react to '%s'"
# Displayed when a user removes a reaction to a comment successfully
SUC_REACTDELPOST_ACCEPT = "Reaction removed successfully"
# Displayed when user can't react to the post
ERR_REACTDELPOST_NOPERM = "You may not react to '%s'"
# Displayed when a post does not exist
ERR_POSTEXIST_NULL = "Post with the id '%s' does not exist"
# Displayed when user successfully deleted the post
SUC_POSTDEL_ACCEPT = "You have successfully deleted the '%s' post"
# Displayed when a user can't delete a post
ERR_POSTDEL_NOPERM = "You cannot delete the 's%' post"
# Displays when user successfully locked a post
SUC_POSTLOCK_ACCEPT = "Post has been locked successfully"
# Displayed when a user fails the lock posts check
ERR_POSTLOCK_NOPERM = "You may not lock this post"
# Displays when user successfully unlocked a post
SUC_POSTULOCK_ACCEPT = "Post has been unlocked successfully"
# Displayed when a user fails the unlock posts check
ERR_POSTULOCK_NOPERM = "You may not unlock this post"
# Displays when user successfully pins a post
SUC_POSTPIN_ACCEPT = "Post has been locked successfully"
# Displayed when a user fails the pin posts check
ERR_POSTPIN_NOPERM = "You may not lock this post"
# Displays when user successfully unpins a post
SUC_POSTUPIN_ACCEPT = "Post has been locked successfully"
# Displayed when a user fails the unpin posts check
ERR_POSTUPIN_NOPERM = "You may not lock this post"
# Displayed when a cannot see the post history
ERR_POSTHIST_NOPERM = "You may not view the post history"
# Displayed when a user creates a post successfully
SUC_POSTADD_ACCEPT = "Post successfully created"
# Displayed when user cannot crete a post
ERR_POSTADD_NOPERM = "You are not allowed to post there or the value provided is wrong"
# Displayed when someone comments successfully
SUC_COMADD_ACCEPT = "Successfully added the comment to post '%s'"
# Displayed when someone can't comment
ERR_COMADD_NOPERM = "You are allowed to comment on '%s'"
# Displayed when a user successfully edits a comment
SUC_COMEDIT_ACCEPT = "Comments successfully edited"
# Displayed when a user cannot edit a comment
ERR_COMEDIT_NOPERM = "You may not edit '%s'"
# Displayed when a user reacts to a comment successfully
SUC_REACTADDCOM_ACCEPT = "Reaction added successfully"
# Displayed when user can't react to the post
ERR_REACTADDCOM_NOPERM = "You may not react to '%s'"
# Displayed when user passes backend remove-reaction comment check
SUC_REACTDELCOM_ACCEPT = "Reaction added successfully"
# Displayed when user fails backend remove-reaction comment check
ERR_REACTDELCOM_NOPERM = "You may not react to '%s'"
# Displayed when a user cannot access more comments, shouldn't happen really
ERR_MORECOMVIEW_NOPERM = "Your request to view more comments has been denied you shouldn't" \
                         " really see this contact a developer"
# Displayed when a comment is deleted successfully
SUC_COMDEL_ACCEPT = "Comment deleted successfully"
# Displayed when a user can't delete a comment
ERR_COMDEL_NOPERM = "You may not delete comment '%s'"
# Displayed when a comment does not exist
ERR_COMEXIST_NULL = "Comment with the id '%s' does not exist"
# Displayed when a invalid request is made
ERR_INVALIDREQ = "Invalid request error nr %i"
# Displayed when a user cannot see the comment history
ERR_COMHIST_NOPERM = "You may not view the comment history"
# Displayed when more posts is more than the max posts
WAR_MPOST_INDEXOF = "Page number over the maximum page defaulting to"
# Displayed when email was sent successfully
SUC_EMAIlSEND_ACCEPT = "Email sent successfully"
# Displayed when email was not sent
ERR_EMAILSEND_EMAILERROR = "Failed to send an email verification"
# Displayed on an invalid form when sending a email
ERR_EMAILSEND_INVFORM = "Invalid form"
# Displayed when user tries logging on but is already logged on
INFO_LOGIN_ALREADYLOGEDIN = "You are already logged in, try logging out before logging back in"
# Displayed when user logs in successfully
SUC_LOGIN_ACCEPT = "Successfully logged in"
# Displayed when user credentials are wrong
ERR_LOGINCRED_INVCREDENTIALS = "Invalid login credentials"
# Displayed when a user can't be found with the credentials provided
ERR_ACTUSER_INVUUID = "Cannot find user with this uuid report this error"
# Displayed when user is verified :)
SUC_ACTUSER_ACCEPT = "User was activated successfully"
# Displayed when user cant be verified with a token
ERR_ACTUSER_INVTOKEN = "Could not activate user, this could be due to expired token or changes to your email/password"
# Displayed after a successful profile post
SUC_PRFADD_ACCEPT = "Profile post successfully added"
# Displayed when a user can't make a profile post
ERR_PRFADD_NOPERM = "You are not allowed to make the profile post"
# Displayed when a user tries to browse a topic he does not have access to
ERR_BROWSE_NOPERM = "You cant access this page"
# Displayed on successful user settings save
SUC_USERSET_ACCEPT = "User settings successfully saved"
# Displayed when a user can't save the settings
ERR_USERSET_NOPERMORINVFORM= "Error Unauthorized user or invalid form"
# Displayed when a password reset email does not exist
ERR_PASSRES_NOEMAIl = "The '%s' email does not exist"
# Displayed when a reset token has an invalid uuid
ERR_RESTOK_INVALIDUID = "No such user with the UID that was provided, if you get this erorr report it to an developer"
# Displayed on successful password reset
SUC_RESTOK_ACCEPT = "Password successfully reset"
# Displayed on mismatching passwords
ERR_RESTOK_MISSMATCH = "Password do not match"
# Display when token is invalid
ERR_RESTOK_DENY = "Token check failed (most likely due to expired token)"
# Displayed on successful thread move
SUC_MVTREAD_ACCEPT = "Thread moved successfully"
# Displayed on unsuccessful thread move
ERR_MVTREAD_NOPERM = "You are not allowed to this thread"
# Displayed on successful profile post deletion
SUC_PRFDEL_ACCEPT = "Profile post successfully deleted"
# Displayed on unsuccessful profile post deletion
ERR_PRFDEL_NOPERM = "You are not allowed to delete this post"
# Displayed on successful badge assignment
SUC_BAGADD_ACCEPT = "Badge has been set successfully"
# Displayed when backend auth for can-user-add-badge or form.is_valid fails
ERR_BAGADD_NOPERMORINVFORM = "You are not allowed to set badges or there is an error with your form"
# Displayed when a badge is successfully deleted
SUC_BAGDEL_ACCEPT = "Badge successfully deleted"
# Displayed when user does not have the power to delete a badge
ERR_BAGDEL_NOPERM = "You are not allowed to delete the badge"
# Displayed when a badge is changed successfully
SUC_BAGEDIT_ACCEPT = "Badge has been set successfully"
# Displayed when the form is incorrect or the user does not have permissions
ERR_BAGEDIT_NOPERMORINVFORM = "Error modifying the badge, either you don't have permissions or the request is incorrect"
# Displayed when the action_type is invalid in a request
ERR_NOTSEEN_INVACTION = "Invalid request, please contact a developer"
