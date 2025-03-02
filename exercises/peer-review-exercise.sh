# invite your peer to your repository

# clone the project from your peer
git clone <url>
# go to project folder
cd <name>

# create peer-review branch
git branch peer-review
# check if is created
git branch -a
# switch to peer-review branch
git checkout peer-review
# or create and switch to the branch if it does not exist
git checkout -b peer-review

# make a seperate document for comments
touch review.md
# edit the file 
# or edit the code file
# ....
# add the files you modified
git add review.md 
# commit the file with a message
git commit -m "review comments added"
# push to peer-review brach
git push --set-upstream origin peer-review





