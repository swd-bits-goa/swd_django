import React from 'react';
import SearchBar from 'material-ui-search-bar';
import {withRouter} from 'react-router';
import CSSTransitionGroup from 'react-addons-css-transition-group';

class SearchBarWithAnimation extends React.Component{
	constructor(props){
		super(props);
		this.state = {
			// Search value depends on search route param
    searchText: props.match.params.query
  };
	}

	 getSearch = (e) => {
    this.setState({searchText: e});
    console.log("Pushing to history", e)
    this.props.history.push("/search/" + e )
  }

	render(){
		return(
			<CSSTransitionGroup
		      		transitionName="searchbox"
		      		transitionAppear={true}
		      		transitionAppearTimeout={700}
		      		transitionEnter={false}
		      		transitionLeave={false}>
				<SearchBar
					value={this.state.searchText}
	                onRequestSearch={() => console.log('onRequestSearch')}
	                spellCheck={false}
	                placeholder={"Search by name or ID"}
	                id="searchbar"
	                style={{width:'120%'}}
	                onChange={this.getSearch}/>
	        </CSSTransitionGroup>
		);

	}
}

export default withRouter(SearchBarWithAnimation);
