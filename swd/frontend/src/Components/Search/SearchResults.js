import React from 'react';
import Paper from 'material-ui/Paper';
import {graphql} from 'react-apollo';
import gql from 'graphql-tag';
import CircularProgress from 'material-ui/CircularProgress';


const styles = {
	name: {margin: 5, padding: 15, paddingBottom: 0, fontSize: 21, marginBottom: 0},
}
class SearchResults extends React.Component{
	constructor(){
		super();
		this.state = {
			active: false,
			search: " "
		}
	}
	render(){
		console.log(this.props.search);
		const { loading, error, searchStudent } = this.props.data;
		if(loading)
			return(<div style={{width: '100%', height: '100%',marginLeft: 'auto', marginRight: 'auto'}}><CircularProgress style={{marginLeft: 'auto', marginRight: 'auto'}}/></div>);
		if(error)
			return(<p>{error}</p>);
		console.log(searchStudent[0]);
		return(
			<Students students={this.props.data.searchStudent}/>
			
		);
	}
}

const Students = ({students}) => {
	return students.map((student) => {
		console.log(student);
		return (
			<Paper zDepth={1} style={{borderRadius: 8, margin: 7}}>
				<h3 style={styles.name}>{student.name}</h3>
				<div style={{display: 'flex'}}>
					<div style={{marginLeft: 20}}>
						<h3>ID</h3>
						{student.hostelps!==null?student.hostelps.acadstudent?<h3>Hostel</h3>:<h3>PS Station:</h3>:<span/>}
						{student.hostelps!==null?student.hostelps.acadstudent?<h3>Room no.</h3>:null:<span/>}
						<h3>Branch</h3>
					</div>
					<div style={{marginLeft: 30}}>
						<h3>{student.bitsId}</h3>
						{student.hostelps!==null?student.hostelps.acadstudent?<h3>{student.hostelps.hostel}</h3>:<h3>{student.hostelps.psStation}</h3>:<span/>}
						{student.hostelps!==null?student.hostelps.acadstudent?<h3>{student.hostelps.room}</h3>:null:<span/>}
						<h3>Mathematics</h3>
					</div>
				</div>
			</Paper>
		);
	});
}


const searchStudent = gql`
	query searchStudent($search: String!, $hostel: [String], $branch: [String]){
		searchStudent(search: $search, hostel: $hostel, branch: $branch){
			name
			bitsId
			hostelps{
				room
				hostel
				acadstudent
				psStation
			}
		}
	}
`;

export default graphql(searchStudent, {options: (props) => ({variables: {search: props.search, hostel: props.hostel, branch: props.branch}})})(SearchResults);
