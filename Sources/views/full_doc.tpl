%include('header.tpl')
	<div id="contents">
		<div id="tagline" class="clearfix">
			<h2>{{!doc_data['Title']}}</h2>
			<div>
				{{!doc_data['Body']}}
                <p>
                    <ul style="list-style-type:none">
                      <li>Name: {{!doc_data['User']['DisplayName']}}</li>
                      <li>Reputation: {{!doc_data['User']['Reputation']}}</li>
                      <li>DownVotes: {{!doc_data['User']['DownVotes']}}</li>
                      <li>UpVotes: {{!doc_data['User']['UpVotes']}}</li>
                    </ul> 
                </p>
                <p>
                    <ul style="list-style-type:none">
                    <li><b>Score:</b> {{!doc_data['Score']}}</li>
                    <li><b>Related Links:</b>
                             %for link in doc_data['PostLinks']: 
                                 {{!link}}
                             %end
                    </li>
                    </ul>
                </p>
                <p>
                    <b>Comments:</b>
                        <ul style="list-list-type:none"> 
                        %for comment in doc_data['Comments']:
                        <li>@{{!comment['User']['DisplayName']}}:{{!comment['Text']}}</li>
                        %end
                        </ul>
                </p>
                <p><h2>Answers:</h2></p>
                <p>
                    %for answer in doc_data['Answers']:
                    <b>{{!answer['Body']}}</b>
                        <p>
                        <ul style="list-style-type:none">
                          <li>Name: {{!answer['User']['DisplayName']}}</li>
                          <li>Reputation: {{!answer['User']['Reputation']}}</li>
                          <li>DownVotes: {{!answer['User']['DownVotes']}}</li>
                          <li>UpVotes: {{!answer['User']['UpVotes']}}</li>
                        </ul> 
                     </p>
                    <p>
                        <ul style="list-style-type:none">
                        <li><b>Score:</b> {{!answer['Score']}}</li>
                        <li><b>Related Links:</b>
                                 %for link in answer['PostLinks']: 
                                     {{!link}}
                                 %end
                        </li>
                        </ul>
                    </p>
                    <p>
                    <b>Comments:</b>
                        <ul style="list-list-type:none"> 
                        %for comment in answer['Comments']:
                        <li>@{{!comment['User']['DisplayName']}}:{{!comment['Text']}}</li>
                        %end
                        </ul>
                    </p>
                 </p>
                     %end
			</div>
		</div>
	</div>

%include('footer.tpl')
