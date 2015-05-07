<!DOCTYPE HTML>
<!-- Website template by freewebsitetemplates.com -->
<html>
<head>
	<meta charset="UTF-8">
	<title>Internal Stack Exchange</title>
	<link rel="stylesheet" href="static/style.css" type="text/css">
</head>
<body>
	<div id="header">
		<div>
			<div class="logo">
				<a href="index.html">Internal S.E</a>
			</div>
			<ul id="navigation">
				<li class="active">
					<a href="index.html">Home</a>
				</li>
				<li>
					<a href="help.html">Help</a>
				</li>
				<li>
					<a href="news.html">News</a>
				</li>
				<li>
					<a href="about.html">About</a>
				</li>
				<li>
					<a href="contact.html">Contact</a>
				</li>
			</ul>
		</div>
	</div>
	<div id="contents">
		<div id="tagline" class="clearfix">
			<h1>Welcome. Select a Stack Exchange site:</h1>
			<div>
				<p>
                    (Sort by <a href="/?sort_type=name">Name</a>/<a href="/?sort_type=size">Size</a>)
                  <ul>
                    % for site in s_e_sites:
                    <li>{{site[0]}} ({{site[1]}})</li>
                    % end
                  </ul> 
				</p>
			</div>
		</div>
	</div>
	<div id="footer">
		<div class="clearfix">
			<p>
				© 2023 Zerotype. All Rights Reserved.
			</p>
		</div>
	</div>
</body>
</html>
