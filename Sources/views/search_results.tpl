%include('header.tpl')
	<div id="contents">
		<div id="tagline" class="clearfix">
            <p><a href="/site?site_name={{site_name}}">Back to Site Page</a>
			<h1>Results for: {{search_term}}</h1>
			<div>
                <p>
                    %if prev_page != None:
                    <a href="/search?page_number={{prev_page}}&is_tag={{is_tag}}&site_name={{site_name}}&search_term={{search_term}}">Previous 10 Results</a>
                    %end
                    %if next_page != None: 
                    <a href="/search?page_number={{next_page}}&is_tag={{is_tag}}&site_name={{site_name}}&search_term={{search_term}}">Next 10 results</a><p>
                    %end
                </p>
				<p>
                  <ul>
                    %for result in search_results:
                    <li><h3><i>{{!result['Title']}}</i></h3>
                        {{!result['Body']}}
                        <a href="/display_full_doc?page_number={{current_page_num}}&is_tag={{is_tag}}&search_term={{search_term}}&site_name={{site_name}}&doc_id={{result['Id']}}">More</a>
                    </li>
                    %end
                  </ul> 
				</p>
			</div>
		</div>
	</div>

%include('footer.tpl')
