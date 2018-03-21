import React from 'react';
import TextField from 'material-ui/TextField';
import Filters from './Filters.js';
import SearchResults from './SearchResults.js';
import {graphql} from 'react-apollo';
import gql from 'graphql-tag';

export default class Search extends React.Component{
	constructor(){
		super();
		this.state = {
			hostel: [],
			branch: []
		}
	}
	handleSort = (key, value) => {
		var searchQuery = this.props.searchQuery;
		if(key=="hostel")
			this.setState({hostel: value});
		else if(key=="branch")
			this.setState({branch: value});
		console.log(this.state.hostel);
		console.log(this.props.history);
	}
	render(){
		return(
			<div style={{zIndex: 10, position: 'absolute', top: 65, width: '100%', height: '100%', backgroundColor: 'white', opacity: 1}}>
				<Filters handleSort={this.handleSort.bind(this)}/>
				{/* Check if search query is valid */}
				{this.props.searchQuery?<SearchResults search={this.props.searchQuery} hostel={this.state.hostel} branch={this.state.branch}/>:<SearchResults search="" hostel={this.state.hostel} branch={this.state.branch}/>}
				
			</div>
		);
	}
}