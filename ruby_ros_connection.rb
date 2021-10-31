#BRIEF: This is simply an experiment to develop a protocol
#that accepts user input in a ruby program and publishes
#the user imput to a ROS node via ROS bridge server.

#DEPENDENCIES: must have turtlesim package from the following 
#tutorial: http://wiki.ros.org/ROS/Tutorials

require 'rubygems'
require 'websocket-client-simple'
require 'json'

ws = WebSocket::Client::Simple.connect 'ws://0.0.0.0:9090'

json = File.read('velocity.json')

twist = {
            "op" => "publish", 
            "topic" => "/turtle1/cmd_vel",
            "msg" => 
            [
                "linear" =>
                [
                    "x" => 0.0,
                    "y" => 0.0,
                    "z" => 0.0
                ],
                "angular" =>
                [
                    "x" => 0.0,
                    "y" => 0.0,
                    "z" => 0.0
                ]
            ]

        }
json_doc = JSON.parse(json)

loop do
    #This is where we would take the input from the user in the html file,
    #store the values and send them to a topic. 
    puts "Input Linear Velocity:"
    json_doc["msg"]["linear"]["x"] = gets.chomp.to_f

    puts "Input Angular Velocity:"
    json_doc["msg"]["angular"]["z"] = gets.chomp.to_f

    serialized_json = JSON.generate(json_doc)
    ws.send serialized_json
    sleep 2
end