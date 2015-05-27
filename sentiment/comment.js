/*
 * This file parse the original json file, 
 * calculate sentiment score for each comment 
 * and then write all info to a new json file
 *
 * Usage: node comment.js path_to_input_file
 * Note: You need to install node.js on your laptop/PC
 *       The sentiment package is downloaded from: https://github.com/thisandagain/sentiment
 *       Check this website for more info
 *
 * Author: Wenjun Wang
 * Date: 2015-05-26
 */

/* Import Packages */
var fs = require('fs')
var sentiment = require('sentiment');

var fileName = process.argv[2]
/* Final json file */
var processed = fileName.replace('.json','_processed.json')

fs.writeFile(processed,'[','utf8')

fs.readFile(fileName,'utf8',function(err, data){
	if (err) {
		return console.log('Read Error: ' + err)
	}

	data = JSON.parse(data)

	for (var i = 0; i < data.length; i++){
		fs.appendFile(processed,'[','utf8')
		var entity = data[i]
		for (var j = 0; j < entity.length; j++){
			var comment = entity[j]
			var body = comment['body']
			/* Get sentiment score */
			var score = sentiment(body)
			var text = JSON.stringify(comment)
			/* Info write to final json file */
			text = text.replace('}',',')
			text += '"sentiment":' + '"' + score['score'] + '"}'
			fs.appendFile(processed,text,'utf8')
		}
		fs.appendFile(processed,']','utf8')
	}
	fs.appendFile(processed,']','utf8')
});
