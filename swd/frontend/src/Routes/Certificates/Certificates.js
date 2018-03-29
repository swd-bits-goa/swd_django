import React from 'react';
import Paper from 'material-ui/Paper';
import SelectField from 'material-ui/SelectField';
import MenuItem from 'material-ui/MenuItem';
import TextField from 'material-ui/TextField';
import RaisedButton from 'material-ui/RaisedButton';

const styles = {
    container: {
        minHeight: 600
    },
    formContainer: {
        margin: 5,
        borderRadius: 7,
    },
    header: {
        fontFamily: 'Open Sans',
        padding: 20,
        paddingLeft: 30,
        marginBottom: 0,
        paddingBottom: 0
    },
    dropdown: {
        marginLeft: 30,
        width: '85%'
    },
    textField: {
        marginLeft: 30,
        width: '85%'
    },
    submitButton: {
        width: '50%',
        margin: 15,
        marginBottom: 8,
        marginLeft: '25%'
    }
}

export default class Certificates extends React.Component{
    constructor(){
        super();
        this.state = {
            value: 1,
          };
    }
    handleChange = (event, index, value) => this.setState({value});
    render(){
        return(
            <div style={styles.container}>
            <Paper zDepth={1} style={styles.formContainer}>
                <h2 style={styles.header}>Apply for bonafide certificate</h2>
                <SelectField
                    floatingLabelText="Reason"
                    hintText="Reason"
                    value={this.state.value}
                    onChange={this.handleChange}
                    style={styles.dropdown}
                    labelStyle={{fontSize: 21}}
                    >
                    <MenuItem value={1} primaryText="Bank loan" />
                    <MenuItem value={2} primaryText="Passport" />
                    <MenuItem value={3} primaryText="Other" />
                </SelectField>
                <TextField
                    hintText="Please mention if other reason"
                    style={styles.textField}
                    multiLine={true}/>
                <RaisedButton label="Submit" primary={true} style={styles.submitButton} />
            </Paper>
            <Paper zDepth={1} style={styles.formContainer}>
                <h2 style={styles.header}>Bonafide Applications</h2>
                <div style={{display: 'flex'}}>
                    <div>No.</div>
                    <div>Reason</div>
                    <div>Status</div>
                </div>
            </Paper>
            </div>
        )
    }
}

