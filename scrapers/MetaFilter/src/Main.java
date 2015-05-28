import java.io.IOException;
import java.text.ParseException;

import org.json.JSONException;


public class Main {

	public static void main(String[] args) throws IOException, JSONException, ParseException {
		// TODO Auto-generated method stub
		if(args.length < 1) {
			System.err.println("Usage: java Main timestamp(2014-05-11");
		}
		
		Crawler c = new Crawler(args[0]);
		System.out.println(args[0]);
		c.run();
	}

}
