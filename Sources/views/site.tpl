%include('header.tpl')
	<div id="contents">
		<div id="tagline" class="clearfix">
			<h1>{{site_name}}</h1>
			<div>
				<p>
                    (Sort by <a href="/site?site_name={{site_name}}&sort_type=name">Name</a>/
                             <a href="/site?site_name={{site_name}}&sort_type=size">Size</a>)
                  <ul>
                    % for tag in site_tags:
                    <li><a href="/search?site_name={{site_name}}&tag={{tag[0]}}">{{tag[0]}}</a> ({{tag[1]}})</li>
                    % end
                  </ul> 
				</p>
			</div>
		</div>
	</div>

%include('footer.tpl')
