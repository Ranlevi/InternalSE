%include('header.tpl')
	<div id="contents">
		<div id="tagline" class="clearfix">
            <a href="/site?site_name={{site_name}}">Back to Site Page</a><br>
            <a href="/search?page_number={{page_number}}&is_tag={{is_tag}}&site_name={{site_name}}&search_term={{search_term}}">Back to Search Results</a><br>
            <p>
			    <h2><i>{{!doc_data['Title']}}</i></h2>
			    <div>
				    {{!doc_data['Body']}}
                    <p>
                        <b>Name:</b> {{!doc_data['User']['DisplayName']}} 
                        <b>Reputation:</b> {{!doc_data['User']['Reputation']}}
                        <b>DownVotes:</b> {{!doc_data['User']['DownVotes']}}
                        <b>UpVotes:</b> {{!doc_data['User']['UpVotes']}}
                    </p>
                    <p>
                        <b>Score:</b> {{!doc_data['Score']}}
                        <b>Related Links:</b>
                            %for link in doc_data['PostLinks']: 
                                <a href="/display_full_doc?page_number={{page_number}}&is_tag={{is_tag}}&site_name={{site_name}}&search_term={{search_term}}&doc_id={{link['RelatedPostId']}}">Link</a>,
                            %end
                        
                    </p>
                    <p>
                        <b>Comments:</b>
                            <ul style="list-list-type:none"> 
                                %for comment in doc_data['Comments']:
                                <li id="comments"><b>@{{!comment['User']['DisplayName']}}:</b> {{!comment['Text']}}</li>
                                %end
                            </ul>
                    </p>
                    <p><h2>Answers:</h2></p>
                    <p>
                            %for answer in doc_data['Answers']:
                            <hr>
                            {{!answer['Body']}}
                    </p>
                                <p>
                                    <b>Name:</b> {{!answer['User']['DisplayName']}} 
                                    <b>Reputation:</b> {{!answer['User']['Reputation']}}
                                    <b>DownVotes:</b> {{!answer['User']['DownVotes']}}
                                    <b>UpVotes:</b> {{!answer['User']['UpVotes']}}
                                </p>
                                <p>
                                    <b>Score:</b> {{!answer['Score']}}
                                    <b>Related Links:</b>
                                             %for link in answer['PostLinks']: 
                                                <a href="/display_full_doc?page_number={{page_number}}&is_tag={{is_tag}}&site_name={{site_name}}&search_term={{search_term}}&doc_id={{link['RelatedPostId']}}">Link</a>,
                                             %end
                                </p>
                                <p>
                                    <b>Comments:</b>
                                        <ul style="list-list-type:none"> 
                                            %for comment in answer['Comments']:
                                            <li id="comments"><b>@{{!comment['User']['DisplayName']}}:</b> {{!comment['Text']}}</li>
                                            %end
                                        </ul>
                                </p>
                            % end
			    </div>
            </p>
		</div>
	</div>

%include('footer.tpl')
