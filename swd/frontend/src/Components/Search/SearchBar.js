import React from 'react';
import SearchBar from 'material-ui-search-bar';
import CSSTransitionGroup from 'react-addons-css-transition-group';

export default class SearchBar1 extends React.Component{
	constructor(){
		super();
	}
	/*handleChange(e){
		if(e != ""){
			this.setState({active: true, search: e});
		}
		else{
			this.setState({active: false, search: e});
		}
		const { fetchMore } = this.props.data;
		console.log('alri');
	}*/

	render(){
		return(
			<CSSTransitionGroup
		      		transitionName="searchbox"
		      		transitionAppear={true}
		      		transitionAppearTimeout={700}
		      		transitionEnter={false}
		      		transitionLeave={false}>
				<SearchBar
	                onChange={this.handleChange}
	                onRequestSearch={() => console.log('onRequestSearch')}
	                spellCheck={false}
	                placeholder={"Search by name or ID"}
	                id="searchbar"
	                style={{width:'120%'}}
	                onChange={this.props.getSearch}/>
	        </CSSTransitionGroup>
		);

	}
}


