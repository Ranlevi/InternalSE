%include('header.tpl')
	<div id="contents">
		<div id="tagline" class="clearfix">
            <p><a href="/index">Back to Sites List</a>
			<h1>{{site_name}}</h1>
			<div>
                 <form action="/search" method="GET">
                    Free Search:<br>
                    <input type="text" name="search_term">
                    <input type="hidden" name="site_name" value="{{site_name}}">
                    <input type="hidden" name="tag" value="">
                    <input type="hidden" name="is_tag" value="0">
                    <input type="submit" value="Submit">
                 </form> 
   				  <p><h3>Tags:</h3><br>
                    (Sort by <a href="/site?site_name={{site_name}}&sort_type=name">Name</a>/
                             <a href="/site?site_name={{site_name}}&sort_type=size">Size</a>)
                  <ul>
                    % for tag in site_tags:
                    <li><a href="/search?is_tag=1&site_name={{site_name}}&search_term={{tag[0]}}">{{tag[0]}}</a> ({{tag[1]}})</li>
                    % end
                  </ul> 
				</p>
			</div>
		</div>
	</div>

%include('footer.tpl')
