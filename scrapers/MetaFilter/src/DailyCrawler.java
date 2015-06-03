import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.text.DateFormat;
import java.text.DateFormatSymbols;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Collections;
import java.util.Comparator;
import java.util.Date;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.StringTokenizer;
import java.util.TreeSet;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.jsoup.Connection;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;



public class DailyCrawler {
	
	static final String path = "/Users/Yao/Desktop/MITS_Project/Weiss/scrapers/MetaFilter/data/";
	
	
	String timeString = "";
	String time4Search = "";
	String month = "";
	String day = "";
	String year = "";
	String monthString = "";
	
	List<String> linkList = new LinkedList<String>(); //Link list
	JSONArray entities = new JSONArray(); //Entity list
	JSONArray commentEntityArray = new JSONArray(); //Comments in each entity
	JSONArray commentArray; //Comments list
	
	HashMap<String, String> url2ID = new HashMap<String, String>(); //The map between article url and EID
	HashMap<String, Integer> history2 = new HashMap<String, Integer>(); //The history of day before yesterday
	HashMap<String, Integer> history1 = new HashMap<String, Integer>(); //The history of yesterday
	HashMap<String, Integer> historyToday = new HashMap<String, Integer>(); //The history of yesterday
	
	/**
	 * @brief Constructor
	 * @param timeString
	 */
	DailyCrawler(String timeString) {
		this.timeString = timeString;
		String[] args = timeString.split("-");
		year = args[0];
		month = args[1];
		day = args[2];
		monthString = new DateFormatSymbols().getMonths()[Integer.parseInt(month) - 1]; // array starts from 0
		//System.out.println(timeString);
		//System.out.println(monthString);
	}
	
	public void run() throws IOException, JSONException, ParseException {
		System.out.println("**************Load History**************");
		loadHistory(1); //Load yesterday history
		loadHistory(2); //Load the history of the day before yesterday
		System.out.println("**************Update History**************");
		updateHistory(1); //System.out.println("load history1:"+history1.size());
		updateHistory(2); //System.out.println("load history1:"+history2.size());
		System.out.println("**************Fetch Daily Data**************");
		fetchToday();
		storeBack2Disk();
	}

	public void loadHistory(int historyOpt) {
		HashMap<String, Integer> temp;
		if(historyOpt == 2)
			temp = history2;
		else
			temp = history1;
		
		try {
			FileReader file = new FileReader(path+ "history"+historyOpt);
			BufferedReader buff = new BufferedReader(file);
			boolean eof = false;
			
			while (!eof) {
				String line = buff.readLine();
				if (line == null)
						eof = true;
				else {
					String id = line.split("\t")[0];
					String url = line.split("\t")[1];
					int comment = Integer.parseInt(line.split("\t")[2]);
					temp.put(url, comment);
					url2ID.put(url,id);
					System.out.println(url);
				}
			}
			buff.close();
		} catch(IOException e) {
			e.printStackTrace();
		}
	}
	
	public void updateHistory(int historyOpt) throws IOException {
		HashMap<String, Integer> temp;
		if(historyOpt == 2)
			temp = history2;
		else
			temp = history1;
		TreeSet<String> s = new TreeSet(new URLComparator());
		s.addAll(temp.keySet());
		
		for(String url:s) {
		
			int commentNo = temp.get(url);
			int count = 0;
			
			Connection conn= Jsoup.connect(url).timeout(10*1000);
			String html  = conn.get().html(); 
			/** Extract each comment */
			String commentFS = "<div class=\"comments\">";
			String commentFE = "<span";
			
			/** Check unlogged in issue at tail */
			String tail = html.substring(html.lastIndexOf(commentFS));
			if(tail.contains("You are not currently logged in")) {
				html = html.substring(0,html.lastIndexOf(commentFS));
			} else {
			}
			
			Document doc = Jsoup.parse(html);
			Elements comments = doc.select("div.comments");
			
			//System.out.println("Total Comment number:"+comments.size() + ";" + "Previous Comment number:"+commentNo);
			if(comments.size() == commentNo) {
				System.out.println(url2ID.get(url) + "\t" + url + "\t" + " No new Comment");
				continue;
			} else {
				
				// skip historical comments
				for(int i = 0 ; i < commentNo ; i ++)
					comments.remove(0);
			}
			
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
					Comment c = new Comment(url2ID.get(url).toString(),timeString,username.text(),"",commentBody);
					JSONObject cJson = c.convert2Json();
					count++;
					this.commentArray.put(cJson);
					//System.out.println("comment:\n" + cJson.toString());
				} catch(Exception e)  {
					// ignore this illegal comment
				}
			}
			
			// Update comment number
			temp.put(url, temp.get(url)  + count );
			System.out.println(url2ID.get(url) + "\t" + url + "\t" + temp.get(url));
		}
	}

	public void fetchToday() throws IOException, JSONException, ParseException {
		if(getLinkList()) {
			processLink();
			System.out.println("Daily Data");
			System.out.println("New Entity:"+this.entities.length());
		}
	}
	
	public boolean getLinkList() throws IOException {
		
		Connection conn= Jsoup.connect("http://www.metafilter.com/").timeout(10*1000);
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
			
			if(history1.containsKey(url) == false && history2.containsKey(url) == false ) {
				// add into list
				linkList.add(url);
				//System.out.println(url);
			} else {
				return linkList.size() > 0;
			}
			html = html.substring(indexE + linkEnd.length());
		}
		
		//System.out.println(html);
		return linkList.size() > 0;
	}

	private void processLink() throws IOException, JSONException, ParseException {
		while(linkList.size() > 0) {
			
			String url = linkList.remove(0);
			String eid = url.split("/")[3];
			//Put it into url2ID
			url2ID.put(url, eid);
			
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
		processComment(url, html,entity);
	}
	
	private void processComment(String url, String html, 
			JSONObject entity) throws ParseException, JSONException {
		/** Extract each comment */
		String commentFS = "<div class=\"comments\">";
		String commentFE = "<span";
		Document doc = Jsoup.parse(html);
		Elements comments = doc.select("div.comments");
		int count = 0;
		
		/** Check unlogged in issue at tail */
		String tail = html.substring(html.lastIndexOf(commentFS));
		if(tail.contains("You are not currently logged in")) {
			html = html.substring(0,html.lastIndexOf(commentFS));
		} else {
		}
		
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
				count++;
				//System.out.println("comment:\n" + cJson.toString());
			} catch(Exception e)  {
				// ignore this illegal comment
			}
		}
		
		// put it into Today history
		historyToday.put(url, count);
		System.out.println(this.url2ID.get(url)+"\t"+url+"\t" + count);
	}

	private void storeBack2Disk() {
		history2 = history1;
		history1 = this.historyToday;
		TreeSet<String> history = new TreeSet<String>(new URLComparator());
		FileWriter file;
		int commentCount = 0;
		String id;
		
		try {
			
			/** Update history 2 - the day before yesterday to yesterday */
			file = new FileWriter(path+"history2");
			history.addAll(history2.keySet());
			for(String url: history) {
				commentCount = history2.get(url);
				id = this.url2ID.get(url);
				file.write(id + "\t" + url + "\t" + commentCount + "\n");
			}
			file.close();
			history.clear();
			
			/** Update history 1 - yesterday to today */
			file = new FileWriter(path+"history1");
			history.addAll(history1.keySet());
			for(String url: history) {
				commentCount = history1.get(url);
				id = this.url2ID.get(url);
				file.write(id + "\t" + url + "\t" + commentCount + "\n");
			}
			file.close();
			
			
			/** Store today's new entity and new comments to disk */
			// Write All Stuff into file
			FileWriter fstreamComment = new FileWriter(path + "MF_comments_"+ timeString + ".json",true); 
			commentEntityArray.write(fstreamComment);
			fstreamComment.close();
			
			// Create Entities File
			FileWriter fstreamEntity = new FileWriter(path + "MF_entities_"+ timeString + ".json", true);
			entities.write(fstreamEntity);
			fstreamEntity.close();
			
		} catch (IOException e) {
			e.printStackTrace();
		} catch (JSONException e) {
			e.printStackTrace();
		}
	}

	class URLComparator implements Comparator<String>{
		@Override
		public int compare(String url1, String url2) {
			int id1 = Integer.parseInt(url1.split("/")[3]);
			int id2 = Integer.parseInt(url2.split("/")[3]);
			return id2 - id1;
		}
	}

}
