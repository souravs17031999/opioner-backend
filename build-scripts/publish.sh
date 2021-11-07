echo "----- SENDING NOTIFICATION TO SLACK "

echo "---------- $JOB_NAME"
echo "---------- $BRANCH_NAME"

python build-scripts/publish.py