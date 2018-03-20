import React from 'react';
import SelectField from 'material-ui/SelectField';
import MenuItem from 'material-ui/MenuItem';
import Paper from 'material-ui/Paper';
import FilterChips from './FilterChips';

const hostels = [
    'CH1',
    'CH2',
    'CH3',
    'CH4',
    'CH5/CH6',
    'CH7',
    'AH1',
    'AH2',
    'AH3',
    'AH4',
    'AH5',
    'AH6',
    'AH7',
    'AH8',
    'AH9',
];

const branch = [
    'CHEMICAL',
    'PHYSICS',
    'E.E.E',
    'Mechanical',
    'Computer Science',
    'E.N.I',
    'BIOLOGY',
    'CHEMISTRY',
    'ECONOMICS',
    'MATHEMATICS',
    'E.C.E',
    "PhD.",
    "M.E Computer Science"
];

const branchs = {
    CHEMICAL: "A1",
    "E.E.E": "A3",
    Mechanical: "A4",
    "Computer Science": "A7",
    "E.N.I": "A8",
    BIOLOGY: "B1",
    CHEMISTRY: "B2",
    ECONOMICS: "B3",
    MATHEMATICS: "B4",
    PHYSICS: "B5",
    "E.C.E": "AA",
    "PhD.": "PH",
    "M.E Computer Science": "H1"


}

export default class Filters extends React.Component{
	state = {
    	hostelValues: [],
    	branchValues: []
  	};

  	handleHostelChange = (event, index, hostelValues) => {
        this.setState({hostelValues});
        this.props.handleSort('hostel', hostelValues);
    }
  	handleBranchChange = (event, index, branchValues) => {
        this.setState({branchValues});
        var branchArray = branchValues.map((branch) => {
            return branchs[branch]
        })
        this.props.handleSort('branch', branchArray);
    }
    handleDelete = (e) => {
        console.log(e);
        console.log(this.state.hostelValues.indexOf(e));
        if(this.state.hostelValues.find((hostel) => hostel==e)){
            const index = this.state.hostelValues.indexOf(e);
            this.setState({hostelValues: this.state.hostelValues.slice(0,index).concat(this.state.hostelValues.slice(index+1))});
            this.props.handleSort("hostel", this.state.hostelValues.slice(0,index).concat(this.state.hostelValues.slice(index+1)));
        }
        else{
            const index = this.state.branchValues.indexOf(e);
            this.setState({branchValues: this.state.branchValues.slice(0,index).concat(this.state.branchValues.slice(index+1))});
            this.props.handleSort("branch", this.state.branchValues.slice(0,index).concat(this.state.branchValues.slice(index+1)));
        }
        }


  	menuItems(val, values) {
	    return val.map((name) => (
	      <MenuItem
	        key={name}
	        insetChildren={true}
	        checked={values && values.indexOf(name) > -1}
	        value={name}
	        primaryText={name}
            style={{minWidth: 200}}/>
	    ));
  	}

	render(){
		const { hostelValues, branchValues}= this.state;
		return(
            <div>
			<Paper zDepth={1} style={{marginTop: -10}}>
				<div style={{display: 'flex', marginLeft: 30}}>
                        <div style={{maxWidth: 180}}>

                        <SelectField
                                multiple={true}
                                hintText="Filter by Hostel"
                                value={hostelValues}
                                onChange={this.handleHostelChange}
                                floatingLabelText="Hostel"
                                underlineStyle={{display: 'none'}}
                                style={styles.selectHostel}
                                floatingLabelStyle={{color: "#777"}}
                                menuStyle={{marginLeft: -10}}
                                autoWidth={true}
                                listStyle={{position: 'relative', left: -10}}
                        >
                                {this.menuItems(hostels, hostelValues)}
                        </SelectField>
                        </div>
                        <div style={{maxWidth: 180}}>

                        <SelectField
                                multiple={true}
                                hintText="Filter by Degree"
                                value={branchValues}
                                onChange={this.handleBranchChange}
                                floatingLabelText="Degree"
                                underlineStyle={{display: 'none'}}
                                style={styles.selectBranch}
                                autoWidth={true}
                                floatingLabelStyle={{color: "#777"}}>
                                {this.menuItems(branch, branchValues)}
                        </SelectField>
                        </div>
                </div>
			</Paper>
            <FilterChips filters={this.state.hostelValues.concat(this.state.branchValues)} deleteFilters={this.handleDelete.bind(this)}/>
            </div>

		);
	}
}

const styles = {
    selectHostel: {
        marginTop: -15,
        paddingLeft: 15,
        maxWidth: 180
    },
    selectBranch: {
        marginTop: -15,
        paddingLeft: 15,
        maxWidth: 180
    }
}