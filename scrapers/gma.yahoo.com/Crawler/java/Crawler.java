package Crawler.java;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.Writer;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLConnection;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Set;
import java.util.GregorianCalendar;
import java.util.Date;

import org.jsoup.Connection;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;
import org.json.*;;
/**  This Crawler only fetch gma.yahoo.com currently*/

//pagesToVisit.add("https://gma.yahoo.com/baby-gorilla-born-australian-zoo-173635261--abc-news-pets.html");
//&offset=70&pageNumber=7

//https://gma.yahoo.com/_xhr/contentcomments/get_all/
//?content_id=af700e88-8dc7-3e10-8755-4850bfca5b93
//&done=https%3A%2F%2Fgma.yahoo.com%2Fchris-pratt-reveals-actors-used-hit-wife-front-183412883--abc-news-music.html
public class Crawler {
	
	/** All Data Fields */
	private String commentID = "";
	private String entityID = "";
	private String timestamp = "";
	private String commentAuthor = "";
	private String commentTitle = "";
	private String commentBody = "";
	private String source = "";
	
	private int totalComment = 0;
	
	private JSONArray commentEntityArray = new JSONArray(); // for new comments array of each entity
	private JSONArray commentsArray;	// for new comments of each entity
	private JSONArray entitiesArray = new JSONArray(); // for new entities array
	
	private final int MAX_PAGES_TO_SEARCH = 50;
    private Set<String> pagesVisited = new HashSet<String>();
    private List<String> pagesToVisit = new LinkedList<String>();
    
    /** Format */
    DateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd");
    private Date date = new Date();
    
	public void run(String startUrl) throws Exception {
		
		//fetchAllLinks("http://gma.yahoo.com");
		pagesToVisit.add(startUrl);
		while(pagesVisited.size() < MAX_PAGES_TO_SEARCH && pagesToVisit.size() > 0) {
			String newsURL = pagesToVisit.remove(0);
			System.out.println("explore url:" + newsURL);
			processSite(newsURL);
			System.out.println("pagesToVisit:"+pagesToVisit.size());
			System.out.println("pagesVisited:"+pagesVisited.size());
		}
		
		/** Create Comments File */
		FileWriter fstreamComment = new FileWriter(new File(".").getAbsolutePath() 
				+"/data/comments_"+ dateFormat.format(date),true); 
		commentEntityArray.write(fstreamComment);
		
		/** Create Entities File */
		FileWriter fstreamEntity = new FileWriter(new File(".").getAbsolutePath() 
				+"/data/entities_"+ dateFormat.format(date), true);
		entitiesArray.write(fstreamEntity);
		
		fstreamComment.close();
		fstreamEntity.close();
	}
	
	private void fetchAllLinks(String url) throws Exception{
		Document htmlDocument = Jsoup.connect(url).timeout(10*1000).get();
		Elements linksOnPage = htmlDocument.select("a[href]");
		
		for(Element link : linksOnPage)
        {
            String linkURL = link.absUrl("href").toString();
            if(pagesVisited.contains(linkURL) == false && pagesToVisit.contains(linkURL) == false) {
            	// Check if url is valid
            	if(linkURL.matches("https://gma.yahoo.com/.+html") && !linkURL.contains("gma-insider-"))
            		pagesToVisit.add(linkURL);
            	//System.out.println("Found Link:"+linkURL);
            }
        }
	}
	
	private void processSite(String newsURL) throws Exception {
		totalComment = 0;
		String title = "";
		commentTitle = "";
		commentID = "";
		int indexS = 0;
		int indexE = 0;
		boolean flagComment = false;
		
		// get title
		title = newsURL.substring(newsURL.lastIndexOf('/')+1, newsURL.indexOf(".html"));
		
		// get source
		indexS = newsURL.indexOf("//") + 2;
		this.source = newsURL.substring(indexS, newsURL.indexOf('/', indexS));
		
		URL site = new URL(newsURL);
		URLConnection yc = site.openConnection();
		BufferedReader in = new BufferedReader(new InputStreamReader(
		        yc.getInputStream()));
		
		String inputLine = "";
		indexS = 0;
		indexE = 0;
		
		while((inputLine = in.readLine())!= null) {
			
			// get title
			if(commentTitle.equals("") && inputLine.contains("<meta property=\"og:title\" content=\"")){
				indexS = inputLine.indexOf("<meta property=\"og:title\" content=\"") + "<meta property=\"og:title\" content=\"".length();
				indexE = inputLine.indexOf("\"/>",indexS);
				commentTitle = ((String) inputLine.subSequence(indexS, indexE));
			}
			
			// get total Comment number
			if(inputLine.contains("total-comment-count")) {
				indexS = inputLine.indexOf("total-comment-count\">") + "total-comment-count\">".length();
				indexE = inputLine.indexOf("</span>",indexS);
				totalComment = Integer.parseInt((String) inputLine.subSequence(indexS, indexE));
				flagComment = true;
			}
			
			// get content_id
			if(inputLine.contains("CONTENT_ID = \"")) {
				indexS = inputLine.indexOf("CONTENT_ID = \"") + "CONTENT_ID = \"".length();
				indexE = inputLine.indexOf("\"",indexS);
				commentID = ((String) inputLine.subSequence(indexS, indexE));
				this.entityID = commentID;
				
				//Create entity and put into array
				JSONObject entity = new JSONObject();
				entity.put("url", newsURL);
				entity.put("source", this.source);
				entity.put("id", this.entityID);
				entity.put("tid",1);
				entity.put("name", "movie");
				this.entitiesArray.put(entity);
			}
			
			// Assume always can get content_id before comment number
			if(flagComment == true)
				break;
		}
		
		
		System.out.println("totalComment:"+totalComment);
		System.out.println("Title:"+commentTitle);
		System.out.println("Content_id:"+commentID);
		
		if(totalComment > 0) {
			commentsArray = new JSONArray();
			processComment(newsURL, totalComment, title, commentTitle, commentID);
			commentEntityArray.put(commentsArray);
			pagesVisited.add(newsURL);
		}
		
		// Close input stream
		in.close();
		
		// Get all links on the web page
		fetchAllLinks(newsURL);
	}
	
	public void processComment(String newsURL, int totalComment, String title, 
			String realTitle, String content_id) throws IOException, JSONException {
		
		int fetchedComment = 0;
		int i = 0;
		
		/** Get All Comment*/
		while(fetchedComment < totalComment) {
			String url = String.format("https://gma.yahoo.com/_xhr/contentcomments/get_all/"
					+ "?content_id=%s&offset=%d&pageNumber=%d"
					+ "&done=https://gma.yahoo.com/%s",content_id, i*10,i,title);
			//System.out.println("Comment url:"+url);
			URL site = new URL(url);
			URLConnection yc = site.openConnection();
			BufferedReader in = new BufferedReader(new InputStreamReader(
			        yc.getInputStream()));
			
			String inputLine;
			while ((inputLine = in.readLine()) != null) {
				int newComment = processLine(inputLine);
				if(newComment != 0)
					fetchedComment += newComment;
				else {
					in.close();
					return;
				}
			}
			in.close();
			i++;
		}
		//System.out.println("Fetched Comment:" + fetchedComment);
	}
	
	private int processLine(String line) throws IOException, JSONException{
		int indexS = 0;
		int indexE = 0;
		int fetchedComment = 0;
		String flagCS = "<p class=\\\"comment-content\\\">\\n";
		String flagCE = "<\\/p>";
		String flagTimeS = "<span class=\\\"comment-timestamp\\\">";
		String flagTimeE = "<\\/span>";
		String flagUNS = "int profile-link";
		String flagUNE = "<\\/span>";
		String uname = "";
		
 		while(line.contains(flagCS)) {
			// print out comment
			
			// Get username
			indexS = line.indexOf('>', line.indexOf(flagUNS))+1;
			indexE = line.indexOf(flagUNE, indexS);
			this.commentAuthor = line.substring(indexS, indexE ).trim();
			line = line.substring(indexE + flagUNE.length());
			
			// Get timestamp
			indexS = line.indexOf(flagTimeS);
			indexE = line.indexOf(flagTimeE);
			this.timestamp = line.substring(indexS + flagTimeS.length(), indexE);
			this.timestamp = computeRealTime(timestamp);
			line = line.substring(indexE + flagTimeE.length());
			
			// Get comment
			//<p class=\"comment-content\">\n
			indexS = line.indexOf(flagCS) + flagCS.length();
			indexE = line.indexOf(flagCE,indexS);
			commentBody = ((String) line.subSequence(indexS, indexE)).trim();
			line = line.substring(indexE + flagCE.length());
			
			// Add into array
			JSONObject comment = new JSONObject();
			comment.put("body", this.commentBody);
			comment.put("rating", -1);
			comment.put("author", this.commentAuthor);
			comment.put("title", "");
			comment.put("source", this.source);
			comment.put("id", this.entityID);
			comment.put("time", this.timestamp);
			this.commentsArray.put(comment);
			fetchedComment ++;
		}
 		return fetchedComment;
	}
	
	private String computeRealTime(String timestamp) {
		Calendar cal = new GregorianCalendar();
		
		String[] args = timestamp.split(" ");
		int offset = Integer.parseInt(args[0]);
		
		if(args[1].equals("days")) {
			cal.add(Calendar.DAY_OF_MONTH, -offset);
		} else if(args[1].equals("weeks")) {
			cal.add(Calendar.DAY_OF_WEEK_IN_MONTH, -offset);
		} else if(args[1].equals("months")) {
			cal.add(Calendar.DAY_OF_YEAR, -offset);
		}
		
		Date DaysAgo = cal.getTime();
		return dateFormat.format(DaysAgo);
	}
}
