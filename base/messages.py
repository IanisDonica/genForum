#Displayed when a user tries to enter a post that they don't have permision to
ERR_POSTVIEW_DENY = "You cant access this page '%s'"
#Displayed when someone comments succesfully
SUC_COMADD_ACEPT = "Succesfully added the comment to post '%s'"
#Displayed when someone can't comment
ERR_COMADD_DENY = "You are allowed to comment on '%s'"
#Displayed when a user succesfully edits a comment
SUC_COMEDIT_ACEPT = "Comments succesfully edited"
#Displayed when a user cannot edit a comment
ERR_COMEDIT_DENY = "You may not edit '%s'"
#Displayed when a user edits a post succesfully
SUC_POSTEDIT_ACEPT = "Post succesfully edited"
#Displayed when a user cannot edit the post
ERR_POSTEDIT_DENY = "You may not edit '%s'"
#Displayed when a user reacts to a comment succesfully
SUC_REACTADDPOST_ACEPT = "Reaction added succesfully"
#Displayed when user can't react to the post
ERR_REACTADDPOST_DENY = "You may not react to '%s'"
#Displayed when a user reacts to a comment succesfully
SUC_REACTADDCOM_ACEPT = "Reaction added succesfully"
#Displayed when user can't react to the post
ERR_REACTADDCOM_DENY = "You may not react to '%s'"
#Displayed when a user removes a reaction to a comment succesfully
SUC_REACTDELPOST_ACEPT = "Reaction removed succesfully"
#Displayed when user can't react to the post
ERR_REACTDELPOST_DENY = "You may not react to '%s'"
#Displayed when user passes backend remove-reaction comment check
SUC_REACTDELCOM_ACEPT = "Reaction added succesfully"
#Displayed when user fails backend remove-reaction comment check
ERR_REACTDELCOM_DENY = "You may not react to '%s'"
#Displayed when a user cannot access more comments, shouldn't happen really
ERR_MORECOMVIEW_DENY = "Your request to view more comments has been denied you shouldn't really see this contant an developer"
#Displayed when a comment is deleted succesfully
SUC_COMDEL_ACEPT = "Comment deleted succesfully"
#Displayed when a user can't delete a comment
ERR_COMDEL_DENY = "You may not delete comment '%s'"
#Displayed when usser succesfully deleted the post
SUC_POSTDEL_ACEPT = "You have succesfully deleted the '%s' post"
#Displayed when a user can't delete a  post
ERR_POSTDEL_DENY = "You cannot delte the 's%' post"
#Displayed when a post does not exist
ERR_POSTEXIST_DENY = "Post with the id '%s' does not exist"
#Displayed when a comment does not exist
ERR_COMEXIST_DENY = "Comment with the id '%s' does not exist"
#Displays when user succesfully locked a post
SUC_POSTLOCK_ACEPT = "Post has been locked succesfully"
#Displayed when a user fails the lock posts check
ERR_POSTLOCK_DENY = "You may not lock this post"
#Displays when user succesfully unlocked a post
SUC_POSTULOCK_ACEPT = "Post has been unlocked succesfully"
#Displayed when a user fails the unlock posts check
ERR_POSTULOCK_DENY = "You may not unlock this post"
#Displays when user succesfully pins a post
SUC_POSTPIN_ACEPT = "Post has been locked succesfully"
#Displayed when a user fails the pin posts check
ERR_POSTPIN_DENY = "You may not lock this post"
#Displays when user succesfully unpins a post
SUC_POSTUPIN_ACEPT = "Post has been locked succesfully"
#Displayed when a user fails the unpin posts check
ERR_POSTUPIN_DENY = "You may not lock this post"
#Displayed when a invalid request is made
ERR_INVALIDREQ = "Invalid request error nr %i"
#Displayed when a user cannot see the comment history
ERR_COMHIST_DENY = "You may not view the comment history"
#Displayed when a cannot see the post history
ERR_POSTHIST_DENY = "You may not view the post history"
#Displayed when more posts is more then the max posts
WAR_MPOST_WAR = "Page number over the maximum page defaulting to"
#Displayed when email was sent succesfully
SUC_EMAIlSEND_ACEPT = "Email sent succesfully"
#Displayed when email was not sent
ERR_EMAILSEND_DENY = "Failed to send an email verification"
#Displayed when user tries logging on but is already loged on
INFO_LOGIN_DENY = "You are already loged in, try logging out before logging back in"
#Displayed when user logs in succesfully
SUC_LOGIN_ACEPT =  "Succesfully loged in"
#Displayed when user credentials are wrong
ERR_LOGINCRED_DENY = "Invalid login credentials"
#Displayed when a user can't be found with the credentials provided
ERR_ACTUSERUUID_DENY = "Cannot find user with this uuid report this error"
#Displayed when user is verified :)
SUC_ACTUSER_ACEPT = "User was activated succesfully"
#Displayed when user cant be verified with a token
ERR_ACTUSER_DENY = "Could not activate user, this could be due to expired token or changes to your email/password"
#Displayed when a user creates a post succesfully
SUC_POSTADD_ACEPT = "Post succesfully created"
#Displayed when user cannot crete a post
ERR_POSTADD_DENY = "You are not allowed to post there or the value provided is wrong"
#Displayed after a succesfull profile post
SUC_PRFADD_ACEPT = "Profile post succesfully added"
#Displayed when a user can't make a profile post
ERR_PRFADD_DENY = "You are not allowed to make the profile post"
#Displayed when a user ries to browse a topic he does not have access to
ERR_BROWSE_DENY = "You cant acces this page"
#Displayed on succesfull user settings save
SUC_USERSET_ACEPT = "User settings succesfully saved"
#Displayed when a user can't save the settings
ERR_USERSET_DENY = "Error Unorthorized user or invalid form"
#Displayed when a password reset email does not exist
ERR_PASSRES_NOEMAIl = "The '%s' email does not exist"
#Displayed when a resettoken has a invalid uuid
ERR_RESTOK_INVALIDUID = "No such user with the UID that was provided, if you get this erorr report it to an developer"
#Displayed on succesfull password reset
SUC_RESTOK_ACEPT = "Password succesfully reset"
#Displayed on missmatching passwords
ERR_RESTOK_MISSMATCH = "Password do not match"
#Display when token is invalid
ERR_RESTOK_DENY = "Token check failed (most likely due to expired token)"
#Displayed on succesfull thread move
SUC_MVTREAD_ACEPT = "Thread moved succesfully"
#Displayed on unsuccesfull thread move
ERR_MVTREAD_DENY = "You are not allowed to this thread"
#Displayed on succesfull profile post deletion
SUC_PRFDEL_ACEPT = "Profile post succesfully deleted"
#Displayed on unsuccesfull profile post deletion
ERR_PRFDEL_DENY = "You are not allowed to delete this post"
#Displayed on succesfull badge asignment
SUC_BAGADD_ACEPT = "Badge has been set successfully"
#Displayed when backend auth for can-user-add-badge or form.is_valid fails
ERR_BAGADD_DENY = "You are not allowed to set badges or there is an error with your form"
#Displayed when a badge is succesfully delted
SUC_BAGDEL_ACEPT = "Badge successfully deleted"
#Displayed when user does not have the power to delete a badge
ERR_BAGDEL_DENY = "You are not allowed to delete the badge"
#Displayed when a badge is changed succesfully
SUC_BAGEDIT_ACEPT = "Badge has been set successfully"
#Displayed when the form is incorect or the user does not have permisions
ERR_BAGEDIT_DENY = "Error modifying the badge, either you don't have permisions or the request is incorect"