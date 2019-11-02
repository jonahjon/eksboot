npm install -g aws-cdk
cdk --version
pip install --upgrade aws-cdk.core
cdk init sample-app --language=python
python3 -m venv .env
source .env/bin/activate
pip3 install -r requirements.txt
pip3 install aws-cdk.aws-s3
cdk synth
cdk deploy <stack name>