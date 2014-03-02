package raspberrypiarduinoclient;

import java.io.*;
import java.net.*;

public class RaspberryPiArduinoClient {

    static DataOutputStream outToServer;
    static Socket clientSocket;

    static enum Commands {
        clear,
        cursor1,
        cursor2,
        loadsymbol,
        ramsymbol,
        tempsymbol,
        downloadsymbol
    }

    public static void main(String[] args) {
        try {
            clientSocket = new Socket("192.168.0.10", 5005);
            outToServer = new DataOutputStream(clientSocket.getOutputStream());
            SendCommand(Commands.loadsymbol);

            while (true)
            {
                
            }
        } catch (Exception e) {
        }
    }

    static void SendCommand(Commands Command) {
        SendData(Command.toString());
    }

    static void SendData(String data) {
        try {
            outToServer.write((data + '\n').getBytes());
        } catch (Exception e) {
        }
    }
}
