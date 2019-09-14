# Running the below command directly results in the following error
# gifsicle:<stdin>: is a terminal

# wrap it in a bash script instead
gifsicle -d "${1}" -O2 ${2}/* --loop=0 -o "${3}"

