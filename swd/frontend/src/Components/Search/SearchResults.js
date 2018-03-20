import React from 'react';
import Paper from 'material-ui/Paper';
import {graphql} from 'react-apollo';
import gql from 'graphql-tag';
import CircularProgress from 'material-ui/CircularProgress';

const branch = {
    'A1': 'B.E.(Hons) Chemical Engineering',
    'A3': 'B.E.(Hons) Electrical and Electronics Engineering',
    'A4': 'B.E.(Hons) Mechanical Engineering',
    'A7': 'B.E.(Hons) Computer Science',
    'A8': 'B.E.(Hons) Electronics and Instrumentation Engineering',
    'B1': 'MSc. (Hons) Biology',
    'B2': 'MSc. (Hons) Chemistry',
    'B3': 'MSc. (Hons) Economics',
    'B4': 'MSc. (Hons) Mathematics',
    'B5': 'MSc. (Hons) Physics',
    'AA': 'B.E.(Hons) Electronics and Communication Engineering',
    'PH': 'PhD.',
    'H1': 'M.E. (Hons) Computer Science',

}

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
			return(<p>{error.message}</p>);
		console.log(searchStudent[0]);
		return(
			<Students students={this.props.data.searchStudent}/>
			
		);
	}
}

const Students = ({students}) => {
	return students.map((student) => {
		console.log(student.bitsId.substr(4,6));
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
						<p>{student.bitsId}</p>
						{student.hostelps!==null?student.hostelps.acadstudent?<p>{student.hostelps.hostel}</p>:<p>{student.hostelps.psStation}</p>:<span/>}
						{student.hostelps!==null?student.hostelps.acadstudent?<h3>{student.hostelps.room}</h3>:null:<span/>}
						<h3>{branch[student.bitsId.substr(4,2)]}</h3>
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
