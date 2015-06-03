import org.apache.commons.cli.*;

import java.io.IOException;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.Locale;

import org.json.JSONException;
import org.apache.commons.cli.ParseException;

public class Main {

	public static void main(String[] args) throws IOException, JSONException{
		//Set up arguments
		Options options = new Options();
		options.addOption("M","mode",true, "daily or duration");
		options.addOption("S","start",true, "the start date of duration");
		options.addOption("E","end",true, "the end date of duration");
		options.addOption("D","date",true, "a single date for daily job");
		
		HelpFormatter formatter = new HelpFormatter();
		// Try to parse the command line arguments
		String mode = "";
		String startDate = "";
		String endDate = "";
		String date = "";
		DateFormat format = new SimpleDateFormat("yyyy-MM-dd", Locale.ENGLISH);
		
		try {
			CommandLineParser parser = new DefaultParser();
			CommandLine line = parser.parse(options, args);
			if(line.hasOption("mode")) {
				/** Parse Mode */
				mode = line.getOptionValue("mode");
				//System.out.println(line.getOptionValue("mode"));
				if(mode.equals("daily")) {
					/** Daily Job */
					Date d = new Date();
					date = format.format(d);
					DailyCrawler dailyCrawler= new DailyCrawler(date);
					dailyCrawler.run();
					//System.out.println(date);
				} else if(mode.equals("duration")) {
					/** Duration job */
					startDate = line.getOptionValue("start");
					endDate = line.getOptionValue("end");
					
					/** Generate calendar from beginning to end */
					ArchiveCrawler ArCrawler;

					Date startD = format.parse(startDate);
					Date endD = format.parse(endDate);
					
					Calendar calTemp = Calendar.getInstance();
					calTemp.setTime(startD);
					
					Calendar calEnd = Calendar.getInstance();
					calEnd.setTime(endD);
					
					/** Go through each day */
					while(calTemp.after(calEnd) == false) {
						ArCrawler = new ArchiveCrawler(format.format(calTemp.getTime()));
						ArCrawler.run();
						calTemp.add(Calendar.DATE, 1);
					}
					
					//System.out.println(startDate);
					//System.out.println(endDate);
				} else {
					formatter.printHelp( "ant", options, true );
					printSampleCMD();
				}
			} else {
				formatter.printHelp( "ant", options, true );
				printSampleCMD();
			}
		} catch(ParseException exp) {
			System.out.println( "Unexpected exception:" + exp.getMessage() );
		} catch (java.text.ParseException e) {
			System.out.println( "Unexpected exception: Incorrect input for date");
			formatter.printHelp( "ant", options, true );
			printSampleCMD();
		}
	}
	
	public static void printSampleCMD() {
		System.out.println("Sample Command:");
		System.out.println("\tjava program -M duration --start=2015-02-01 --end=2015-02-02");
		System.out.println("\tjava program -M daily");
	}

}
