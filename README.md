# NIDM-Results-neo4j

Testing NIDM-Results Turtle as a [neo4j graph](http://neo4j.com/)
[Here is the result!](http://gist.neo4j.org/?github-vsoch%2Fnidm-neo4j%2F%2Fgist%2Fgraph.gist)

#### 0. Generating your own

use [create_gist.sh](create_gist.sh) to re-generate the example. Note that I specify a github repo name, a user name, and an output folder. The example queries are hard-coded, however the neo4j gist has an interactive console, so this isn't an issue.

Also note that to generate this gist I used functions from the [nidmviewer]() package to parse the RDF. These are in development and don't even use sparql. It would be ideal to move away from having to use RDF, period.

### To set up your own neo4j server

This script will generate code in cypher that can be rendered automatically via a gist, however if you want to set up your own neo4j server, you can follow the instructions below. For the gist, see the [gist](gist) folder.

#### 1. Download neo4j
the community edition of [neo4j](http://neo4j.com/download/). On linux this means extracting the binary to somewhere on your computer:


      cd $HOME/Downloads
      mv neo4j-community-2.2.5-unix.tar.gz $HOME/Packages/
      tar -xzvf neo4j-community-2.2.5-unix.tar.gz 
      rm neo4j-community-2.2.5-unix.tar.gz 

#### 2. Add to path 
To add to your path:

      vim ~/.bashrc
      export PATH=$PATH:/home/vanessa/Packages/neo4j-community-2.2.5/bin
      source ~/.bashrc
      which neo4j
      /home/vanessa/Packages/neo4j-community-2.2.5/bin/neo4j

Then start the server

      neo4j start

Open browser to [http://localhost:7474/](http://localhost:7474/) to see the server running.

#### 3. Download 
Set a new password

You will see a login screen, and instructions to log in with the old password, "neo4j." Log in and you will be prompted to set a new password. Don't forget it, you will need it to test the script.

#### 4. Download 
Make sure you have installed `py2neo`, which is the module for working with neo4j from Python.


      pip install py2neo --user


#### 5. Authenticate
You will need to authenticate in python:

      authenticate("localhost:7474", "neo4j", "neo4j")

this is where you will need to change your password to the one you just set. The authentication doesn't happen at this step, it will happen when you try to make the graph:

      graph = Graph()

so if there are authentication errors you will see them at this time point.

You should be able to run through the code, and see that the interface updates. If the interface in the web browser doesn't update, click the circles in the left bar to see your graph nodes (or click monitor) and in the bottom right of the box that shows your graph (db/data) statistics, click the slider that says "auto refresh." Note that if you need to wipe the entire thing any time, just rm -rf db/data.
