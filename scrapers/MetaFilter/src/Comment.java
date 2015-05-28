import org.json.JSONException;
import org.json.JSONObject;


public class Comment {
	public String entityID = "";
	public String timestamp = "";
	public String commentAuthor = "";
	public String commentTitle = "";
	public String commentBody = "";
	public String source = "";
	
	Comment(String eid, String timestamp, String commentAuthor, String commentTitle, String commentBody) {
		this.entityID = eid;
		this.timestamp = timestamp;
		this.commentAuthor = commentAuthor;
		this.commentTitle = commentTitle;
		this.commentBody = commentBody;
		this.source = "MetaFilter";
	}
	
	public JSONObject convert2Json() throws JSONException {
		JSONObject o = new JSONObject();
		o.put("id", this.entityID);
		o.put("source", this.source);
		o.put("time", this.timestamp);
		o.put("author", this.commentAuthor);
		o.put("title", this.commentTitle);
		o.put("body", this.commentBody);
		o.put("sentiment", -1);
		o.put("rating", "");
		return o;
	}
}
