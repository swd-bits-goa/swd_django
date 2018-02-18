import React from 'react';
import Chip from 'material-ui/Chip';


const styles = {
	chip:{
		display:'inline-flex',
		border: '1px solid #00BCD4',
		backgroundColor: 'white',
		marginRight:3,
	},
	container:{
		verticalAlign: 'top',
		maxWidth: 500,
		marginTop: 10,
		overflowX: 'auto',
		overflowY: 'hidden',
		whiteSpace: 'nowrap',
		marginLeft: 5
	},
}

export default class FilterChips extends React.Component{
	handleRequestDelete = () => console.log('delete');
	render(){
		return(
			<div style={styles.container}>
				<Filters filters={this.props.filters} handleRequestDelete={this.handleRequestDelete}/>
			</div>
		);
	}
}

const Filters = (props) => {
	const allFilters = props.filters;
	return allFilters.map( (filter)=> {
		return <Chip 
				style={styles.chip} 
				onRequestDelete={props.handleRequestDelete}
				>
				{filter}</Chip>
	})
}
