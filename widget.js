(function createWidget() {
    const Widget = Object.create({
        create(id){
            //create the CSS styles of the widget
            const style = `
                    :root {
                        --base-color: #585858;
                        --dark-color: #003f7f;
                        --light-color: #fff;
                        --link-color: #09589a;
                        --success-color: #f0f8f1;
                        --warning-color: #fbeeec;
                        --spacing: 16px;
                    }
                    .widgetContainer {
                        display: flex;
                        flex-direction: row;
                    }
                    
                    .buttonAndInput {
                        display: flex;
                        flex-direction: column;
                    }

                    .search-icon {
                        margin-top: 5px;
                        pointer-events: none;
                        color: var( #003f7f);
                        vertical-align: text-top;
                    }
                    
                    .logFrame {
                        border:1px solid #999999; margin:2px; padding:3px;
                        flex: 1 0;
                    }
                    
                    input.text {width:80%;height:40px;padding:6px 12px;line-height:1.42857143;/*background-image:none;*/border:none;border-radius:none;border-bottom:1px solid #ccc;}
                    
                    input[type=search] {-webkit-appearance:textfield;}

                    input, textarea, select {border:1px solid #ccc;font-size:1em;padding:3px;margin:0;vertical-align:middle;}

                    .button {display:block;padding:10px;margin:.75em auto;width:15rem;background: #003f7f;color:#fff;line-height:1.42857143;text-align:center;white-space:nowrap;vertical-align:middle;-ms-touch-action:manipulation;touch-action:manipulation;cursor:pointer;-webkit-user-select:none;-moz-user-select:none;-ms-user-select:none;user-select:none;background-image:none;border:1px solid transparent;border-radius:4px}
                `
                snippet = document.currentScript.innerHTML
                //input the html of the widget defining text area, button, and output list
                const wdg = document.createElement("div");
                wdg.innerHTML = `
                    <head>
                        <title>Search</title>
                        <meta name="description" content="Recipe Search Function">
                        <style>${style}</style>
                    </head>

                    <body>
                        <div class="widgetContainer">
                            <div class="buttonAndInput">
                                <textarea class="text icon-search" type="search" id="input" name="input" maxlength="75" autofocus placeholder="Enter recipe name, ingredient, or keyword..."></textarea>
                                <button id='safe' class='button'>Search</button>
                                <ol id="frame" name="frame"></ol>
                            </div>
                        </div>
                    </body>
                `
                //input the javascript of the widget
                wdg.script = document.createElement("script");
                wdg.script.setAttribute('type', 'module');
                wdg.script.appendChild(document.createTextNode(`
                        //create the converter that takes B64 and makes a bit array
                        const convertB64ToBitArr = (b64Str) => (Uint8Array.from(atob( (b64Str.includes(';base64,') ? (b64Str.split(','))[1] : b64Str) ), (v) => v.charCodeAt(0)) );
                        //use the converter to make a bit array out of the sql WASM dataURL
                        const sql_wasm_typedarray = convertB64ToBitArr(sql_wasm_dataURL);
                        //convert the bit array to a BLOB object
                        const sql_wasm_blob = new Blob([sql_wasm_typedarray], {
                            type: 'application/wasm'
                        });
                        //convert the BLOB object to an object url and input it into the SQL const
                        const SQL = await initSqlJs({
                            locateFile: file => URL.createObjectURL(sql_wasm_blob)
                        });

                    //make the evaluate function run on either hitting the enter key or clicking the search button
                     var safe = document.getElementById('input');
                    safe.addEventListener('keypress', function(event){
                        if(event.key === "Enter"){
                            event.preventDefault();
                            document.getElementById("safe").click();
                        }
                    });

                    document.getElementById('safe').addEventListener('click', evaluate);

                    //define an evaluate function that searches the database and returns the results
                    function evaluate() {
                        //define the output and input elements for ease of use
                        var frame = document.getElementById('frame');
                        var input = document.getElementById('input').value;
                        
                        //get the sqllite database file
                        const xhr = new XMLHttpRequest();
                        
                        //NEED TO CHANGE: You will need to update this link to wherever the docs.db file is being hosted on your embeddable website
                        xhr.open('GET', 'https://pathtoyourwidget.com/docs.db', true);
                        xhr.responseType = 'arraybuffer';
                        //check if an invalid search will be input
                        if(input === "" || input == " "){
                            frame.innerHTML = "Enter a valid search";
                        }
                        else{
                        //open the db to do queries
                        xhr.onload = e => {
                            const uInt8Array = new Uint8Array(xhr.response);
                            const db = new SQL.Database(uInt8Array);
                            //make the query to do full text search
                            var stmt = "SELECT DISTINCT documents.title, documents.url FROM documents JOIN documents_fts ON documents.rowid = documents_fts.rowid WHERE documents_fts MATCH '" + input + "' UNION SELECT DISTINCT documents.title, documents.url FROM documents JOIN documents_fts ON documents.rowid = documents_fts.rowid WHERE documents_fts.title LIKE '%" + input + "%' ORDER BY 1";
                            var messageFinal = '';
                            //run the query and for each row output a formatted version of the title as an ordered list with links
                            db.each(stmt, function(row){
                                var message = row.title;
                                var url = row.url;
                                //NEED TO CHANGE: Will need to edit these message manipulations to match the titles you wish to output
                                message = message.replaceAll('_', ' ');
                                message = message.replace('- Food Product Development Lab | Montana State University', '');
                                //console.log(message);
                                messageFinal += '<a href="' + url + '"><li>' + message +'</li></a>';
                        });
                        //send the row output to the output frame in html
                        if(messageFinal == ""){
                            //NEED TO CHANGE: Will need to change to whatever output you want when no search result appears
                            frame.innerHTML = "No recipes found"
                        }
                        else{
                            frame.innerHTML = messageFinal
                        }
                        }};
                        xhr.send();
                    }
                `))
                wdg.appendChild(wdg.script)
                return wdg;
        }
    });
    //make the widget appear
    const id = `js${ Math.floor((1 + Math.random()) * 0x10000).toString(16).substring(1)}`;

    const myWidgetInstance = Widget.create(id);

    document.write(`<div id= ${ id } ></div>`);
    document.getElementById(id).appendChild(myWidgetInstance);
})();
