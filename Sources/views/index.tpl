%include('header.tpl')
	<div id="contents">
		<div id="tagline" class="clearfix">
			<h1>Welcome. Select a Stack Exchange site:</h1>
			<div>
				<p>
                    (Sort by <a href="/?sort_type=name">Name</a>/<a href="/?sort_type=size">Size</a>)
                  <ul>
                    % for site in s_e_sites:
                    <li><a href="/site?site_name={{site[0]}}">{{site[0]}}</a> ({{site[1]}})</li>
                    % end
                  </ul> 
				</p>
			</div>
		</div>
	</div>

%include('footer.tpl')
