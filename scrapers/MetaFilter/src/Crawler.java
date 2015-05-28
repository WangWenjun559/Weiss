import java.io.BufferedReader;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLConnection;
import java.text.DateFormat;
import java.text.DateFormatSymbols;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.LinkedList;
import java.util.List;
import java.util.Locale;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.jsoup.Connection;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.select.Elements;
import org.jsoup.nodes.Element;

public class Crawler {
	String timeString = "";
	String time4Search = "";
	String month = "";
	String day = "";
	String year = "";
	String monthString = "";
	
	List<String> linkList = new LinkedList<String>();
	JSONArray entities = new JSONArray();
	JSONArray commentEntityArray = new JSONArray();
	JSONArray commentArray;
	
	Crawler(String timeString) {
		this.timeString = timeString;
		String[] args = timeString.split("-");
		year = args[0];
		month = args[1];
		day = args[2];
		monthString = new DateFormatSymbols().getMonths()[Integer.parseInt(month) - 1]; // array starts from 0
		//System.out.println(monthString);
	}
	
	public void run() throws IOException, JSONException, ParseException {
		if(getLinkList()) {
			processLink();
			/** Write All Stuff into file */
			FileWriter fstreamComment = new FileWriter(new File(".").getAbsolutePath() 
					+"./data/comments_"+ timeString,true); 
			commentEntityArray.write(fstreamComment);
			fstreamComment.close();
			
			/** Create Entities File */
			FileWriter fstreamEntity = new FileWriter(new File(".").getAbsolutePath() 
					+"./data/entities_"+ timeString, true);
			entities.write(fstreamEntity);
			fstreamEntity.close();
		}
	}
	
	public boolean getLinkList() throws IOException {
		//http://www.metafilter.com/archived.mefi/12/02/2014/
		System.out.println(String.format("http://www.metafilter.com/archived.mefi/%s/%s/%s/", month, day, year));
		
		Connection conn= Jsoup.connect(String.format("http://www.metafilter.com/archived.mefi/%s/%s/%s/", month, day, year)).timeout(10*1000);
		String html  = "";
		try{
			html = conn.get().html();
		} catch (Exception e) {
			System.out.println("Non exist site - url");
			return false;
		}
		
		// Jump into certain day in certain month
		int indexS = 0;
		int indexE = 0;
		indexS = html.indexOf("<h2 class=\"monthday\">" + this.monthString + " " + Integer.parseInt(day) + "</h2>");
		indexE = html.indexOf("<h2 class=\"monthday\">" + this.monthString + " " + (Integer.parseInt(day)-1) + "</h2>"
				, indexS + this.monthString.length());
		
		//System.out.println("indexS:"+indexS);
		//System.out.println("indexE:" + indexE);
		if(indexS == -1) {
			// No data available for this day
			System.out.println("No data for " + timeString);
			return false;
		}
		
		if(indexE == -1) {
			html = html.substring(indexS);
		} else {
			html = html.substring(indexS, indexE);
		}
		
		// Get all links(articles) for that day
		String linkStart = "<h2 class=\"posttitle front\">";
		String linkEnd = "</h2>";
		indexS = 0;
		indexE = 0;
		
		while(html.indexOf("<h2 class=\"posttitle front\">", indexS) != -1) {
			indexS = html.indexOf(linkStart);
			indexE = html.indexOf(linkEnd,indexS);
			
			//Extract url;
			String url = html.substring(indexS,indexE+linkEnd.length());
			url = "http://www.metafilter.com" + url.split("\"")[3];
			System.out.println(url);
			// add into list
			linkList.add(url);
			html = html.substring(indexE + linkEnd.length());
		}
		
		//System.out.println(html);
		return true;
	}
	
	private void processLink() throws IOException, JSONException, ParseException {
		while(linkList.size() > 0) {
			
			String url = linkList.remove(0);
			String eid = url.split("/")[3];
			//Create entity and add it into array
			JSONObject entity = new JSONObject();
			entity.put("url", url);
			entity.put("source", "MetaFilter");
			entity.put("id", eid);
			entity.put("tid", 1);
			entity.put("name", url.split("/")[4]);
			
			// lack of description;
			this.commentArray = new JSONArray();
			processArticle(url,entity);
			this.entities.put(entity);
			this.commentEntityArray.put(commentArray);
		}
	}
	
	private void processArticle(String url, JSONObject entity) throws IOException, JSONException, ParseException {
		Connection conn= Jsoup.connect(url).timeout(10*1000);
		String html  = conn.get().html();
		
		String descriptionFS = "<meta name=\"twitter:description\" content=\"";
		String descriptionFE = "\">";
		
		int indexS = 0;
		int indexE = 0;
		
		/** Get description */
		indexS = html.lastIndexOf(descriptionFS) + descriptionFS.length();
		indexE = html.indexOf(descriptionFE,indexS);
		String descrition = html.substring(indexS, indexE);
		// add into entity field
		entity.put("description", descrition);
		
		//System.out.println(descrition);
		//html = html.substring(indexE);
		
		/** Extract each comment */
		processComment(html,entity);
	}
	
	public void processComment(String html, JSONObject entity) throws ParseException, JSONException {
		/** Extract each comment */
		String commentFS = "<div class=\"comments\">";
		String commentFE = "<span";
		Document doc = Jsoup.parse(html);
		Elements comments = doc.select("div.comments");
		//System.out.println("number of comment:"+comments.size());
		while(comments.hasText()){
			/** Create new comment */
			try{
				Element comment = comments.remove(0);
				
				String span = comment.select("span").text();
				
				// Get username
				Element username = comment.select("[target=_self]").first();
				
				// Get timetamp 
				//System.out.println(comment.select("span").text());
				String timestamp = comment.select("span").text().substring(span.lastIndexOf("on ")+3);
				if(timestamp.contains("[")) {
					timestamp = timestamp.substring(0, timestamp.indexOf('[')-1);
				}
				
				if(timestamp.contains(",") == false) {
					timestamp = timestamp + ", 2015";
				}
				// Convert time format
				DateFormat format = new SimpleDateFormat("MMMM d, yyyy", Locale.ENGLISH);
				SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd");
				Date date = format.parse(timestamp);
				timestamp = (dateFormat.format(date));
				//System.out.println(dateFormat.format(date));
				
				
				// Get body
				String commentString = comment.toString();
				String commentBody = commentString.substring(commentString.indexOf(commentFS) 
						+ commentFS.length(), commentString.indexOf(commentFE));
				commentBody = commentBody.replace("<br>", "").trim();
				
				/** Construct Comment */
				Comment c = new Comment(entity.get("id").toString(),timeString,username.text(),"",commentBody);
				JSONObject cJson = c.convert2Json();
				this.commentArray.put(cJson);
				//System.out.println("comment:\n" + cJson.toString());
			} catch(Exception e)  {
				// ignore this illegal comment
			}
		}
		
	}
}
