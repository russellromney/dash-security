python3 release.py $1

if [ $? -ne 0 ]; then 
    # The command failed, print an error message 
    echo "Release bump failed with exit status $?" 
    # Exit the script with a non-zero exit status to indicate failure 
    exit 1 
else 
    # The command was successful, print a success message 
    echo "Release bump succeeded with exit status $?" 
    python setup.py sdist
    twine upload dist/dash-security-$(cat /tmp/dash-security-release-version).tar.gz
    gh release create v$(cat /tmp/dash-security-release-version)
fi 
