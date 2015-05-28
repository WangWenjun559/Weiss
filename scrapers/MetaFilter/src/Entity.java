
public class Entity {
	public String id; // not eid, eid will be added automatically incrementally
	public String source = "MetaFilter";
	public String name;
	public int tid = 1;
	public String description;
	public String url;
	
	Entity(String id, String name, String description, String url) {
		this.id = id;
		this.name = name;
		this.description = description;
		this.url = url;
	}
}
