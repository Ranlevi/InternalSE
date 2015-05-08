%include('header.tpl')
	<div id="contents">
		<div id="tagline" class="clearfix">
			<h1>Results for: {{tag_name}}</h1>
			<div>
				<p>
                  <ul>
                    %for result in search_results:
                    <li><h3>{{!result['Title']}}</h3>
                        {{!result['Body']}}
                        <a href="/display_full_doc?doc_id={{result['Id']}}">More</a>
                    </li>
                    %end
                  </ul> 
				</p>
			</div>
		</div>
	</div>

%include('footer.tpl')
