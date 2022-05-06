// Kyle Orcutt


import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class Service {

    private static String readCSS() {
        try {
            BufferedReader br = new BufferedReader(new FileReader("src/template.css"));
            String line;
            String output = "";
            while ((line = br.readLine()) != null)
            {
                output = output + line.replaceAll("\t","").replaceAll("\n","");
            }
            br.close();
            return output;
        }
        catch (IOException e) {
            e.printStackTrace();
            return null;
        }
    }

    private static String substituteCSS(String css, String accentC, String mainC, String font, String border) {
        css = css.replaceAll("_MAIN_COLOUR_", "#" + mainC);
        css = css.replaceAll("_ACCENT_COLOUR_", "#" + accentC);
        css = css.replaceAll("_FONT_FAMILY_", font);
        css = css.replaceAll("_BORDER_STYLE_", border);
        return css;
    }

    private static String verifyHex(String rawInput, String defaultValue) {
        try {
            Long.parseLong(rawInput,16);
            if (rawInput.length() <= 6) {
                return rawInput;
            }
            else {
                return defaultValue;
            }
        }
        catch (Exception e) {
            e.printStackTrace();
            return defaultValue;
        }
    }

    private static String verifyFont(String fontInput, String defaultValue) {
        try {
            fontInput = fontInput.toLowerCase();
            if (fontInput.equals("serif") || fontInput.equals("sans-serif") || fontInput.equals("monospace")) {
                return fontInput;
            }
            else {
                return defaultValue;
            }
        }
        catch (Exception e) {
            e.printStackTrace();
            return defaultValue;
        }
    }

    private static String verifyBorder(String borderInput, String defaultValue) {
        try {
            borderInput = borderInput.toLowerCase();
            boolean isValid = borderInput.equals("dotted") || borderInput.equals("dashed") || borderInput.equals("solid") ||
                              borderInput.equals("double") || borderInput.equals("groove") || borderInput.equals("ridge") ||
                              borderInput.equals("inset") || borderInput.equals("outset") || borderInput.equals("none");

            if (isValid) {
                return borderInput;
            }
            else {
                return defaultValue;
            }
        }
        catch (Exception e) {
            e.printStackTrace();
            return defaultValue;
        }
    }

    public static void webServe(int port) throws IOException {
        ServerSocket server = new ServerSocket(port);
        while(true) {
            // server.accept() is blocking, so your code will stop here until a connection is made
            Socket userConn = server.accept();
            // Buffered Reader for handling the input stream from the user/client
            BufferedReader br = new BufferedReader(new InputStreamReader(userConn.getInputStream()), 1);
            String output = "";
            String line;
            // Read from the buffer until the buffer is empty or the connection closes
            while ((line = br.readLine()) != null) {
                output = output + line;
                if (line.isEmpty()) {
                    break;
                }
            }

            // Print out the input from the user/client
            System.out.println(output);

            String main = parseHeader("main", output);
            String accent = parseHeader("accent", output);
            String font = parseHeader("font", output);
            String border = parseHeader("border", output);

            main = verifyHex(main, "a1a1a1");
            accent = verifyHex(accent, "a9a9a9");
            font = verifyFont(font, "serif");
            border = verifyBorder(border, "solid");

            String css = readCSS();
            css = substituteCSS(css, accent, main, font, border) + "\r\n";

            String response = "HTTP/1.1 200 OK\r\nContent-Type: text/css\r\n\r\n" + css;
            // Write the HTTP message out to the output stream, back to the client/user
            userConn.getOutputStream().write(response.getBytes("UTF-8"));
            userConn.getOutputStream().flush();
            // Flush to make sure the data is sent, and then close the connection and the buffered reader
            userConn.close();
            br.close();
        }
    }

    public static String parseHeader(String variable, String rawInput) {
        String pattern = "GET /.*" + variable + "=(.*?)(?:&| HTTP)";
        Pattern regex = Pattern.compile(pattern);
        Matcher match = regex.matcher(rawInput);

        if(match.find()) {
            return match.group(1);
        }
        else {
            return null;
        }
    }

    public static void main(String[] args) throws IOException {
        // Begins the webserver on the specified port (Port 80 by default)
        webServe(80);
    }

}