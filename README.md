![ADV](https://github.com/deexno/ACTIVE-DIRECTORY-VIEWER/blob/main/src/banner.png?raw=true "ADV")

## WHAT CAN THE ADV DO?
This tool is designed to help administrators get an overview of their Active Directory structure.
![EXAMPLE](https://github.com/deexno/ACTIVE-DIRECTORY-VIEWER/blob/main/src/example.gif?raw=true "EXAMPLE")

## THE INSTALLATION
1. curl https://raw.githubusercontent.com/deexno/ACTIVE-DIRECTORY-VIEWER/main/Dockerfile -o Dockerfile
2. Change the Dockerfile to your specific configuration
3. docker image build -f Dockerfile . -t adv
4. docker container run -p 65535:65535 -d adv
