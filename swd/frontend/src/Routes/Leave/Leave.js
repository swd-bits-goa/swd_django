/* eslint no-unused-vars:0 */

import React from "react";
import {Mobile} from "../../Components/Responsive";
import s from "./Leave.css";
import DatePicker from 'material-ui/DatePicker';
import TimePicker from 'material-ui/TimePicker';
import SelectField from 'material-ui/SelectField';
import MenuItem from 'material-ui/MenuItem';
import TextField from 'material-ui/TextField';
import {Paper, RaisedButton} from "material-ui";
import { Mutation } from "react-apollo";
import {graphql} from 'react-apollo';
import gql from 'graphql-tag'

let DateTimeFormat;
DateTimeFormat = global.Intl.DateTimeFormat;
/*The following code was for checking browser compatibility
if (areIntlLocalesSupported(['fr', 'fa-IR'])) {
    DateTimeFormat = global.Intl.DateTimeFormat;
  } else {
    const IntlPolyfill = require('intl');
    DateTimeFormat = IntlPolyfill.DateTimeFormat;
    require('intl/locale-data/jsonp/fr');
    require('intl/locale-data/jsonp/fa-IR');
  }*/

const styles = {
    customWidth: {
        width: 150,
    },
    errorMessage: {
        padding: 25,
        color: 'red',
        paddingBottom: 0
    }
};

const applyLeave = gql`
    mutation applyLeave($dateTimeStart: DateTime!, $dateTimeEnd: DateTime!,$reason: String!, $corrPhone: String!, $corrAdress: String!, $consent: String!){
        applyLeave(dateTimeStart: $dateTimeStart, dateTimeEnd: $dateTimeEnd, reason: $reason, corrPhone: $corrPhone, corrAdress: $corrAdress, consent: $consent){
            leave{
                id
            }
            
        }
    }
`;

class Leave extends React.Component {
    constructor(){
        super();
        this.state = {
            reason: "None",
            consent: "None",
            other: "",
            dateStart: null,
            timeStart: null,
            dateEnd: null,
            timeEnd: null,
            corrAdress: "",
            corrPhone: "",
            missingFields: false,
            dateTimeStart: null,
            dateTimeEnd: null
        };
    }
   

    handleChange = (event, index, value) => this.setState({reason: value});
    handleChangeConsent = (event, index, consent) => this.setState({consent});

    handleClick() {
        
        //Move this to confirmation Page and generate a Leave ID
    }

    render() {
        return (
            <Mobile>
                <Mutation className={s.container} mutation={applyLeave} errorPolicy="all" onError={(e) => console.log(e)}>
                {(applyLeave, {data, error}) =>
                (
                <Paper zDepth={2}>
                    {error&&console.log(error.message+" "+error.extraInfo+' '+this.props)}
                    <div className={s.container2}>
                        <h3>Apply For Leave:</h3>
                        <DatePicker 
                             hintText="Departure Date"
                             container="inline"
                             formatDate={new DateTimeFormat('en-US', {
                                day: 'numeric',
                                month: 'long',
                                year: 'numeric',
                              }).format}
                             onChange={(e, date) => {this.setState({dateStart: date})}}/>
                        <TimePicker
                            hintText="Departure Time"
                            autoOk={true}
                            onChange={(e, time) => {this.setState({timeStart: time})}}
                        />
                        <DatePicker 
                            hintText="Arrival Date" 
                            container="inline"
                            formatDate={new DateTimeFormat('en-US', {
                                day: 'numeric',
                                month: 'long',
                                year: 'numeric',
                              }).format}
                              onChange={(e, date) => {this.setState({dateEnd: date})}}  />
                        <TimePicker
                            hintText="Arrival Time"
                            autoOk={true}
                            onChange={(e, time) => {this.setState({timeEnd: time})}}
                        />
                        <SelectField
                            floatingLabelText="Reason"
                            value={this.state.reason}
                            onChange={this.handleChange}
                        >
                            <MenuItem value={"None"} primaryText="None"/>
                            <MenuItem value={"Siter's Wedding"} primaryText="Sister's Wedding"/>
                            <MenuItem value={"Brother's Wedding"} primaryText="Brother's Wedding"/>
                            <MenuItem value={"Family Function"} primaryText="Family Function"/>
                            <MenuItem value={"Examination"} primaryText="Examination"/>
                            <MenuItem value={"To stay with parents in Goa"} primaryText="To stay with parents in Goa"/>
                            <MenuItem value={"Festivals"} primaryText="Festivals"/>
                            <MenuItem value={"Other"} primaryText="Other"/>
                        </SelectField>
                        {this.state.reason === "Other" &&
                        <TextField
                            floatingLabelText="Please Specify Reason Here"
                            value={this.state.other}
                            onChange={(e,val) => this.setState({other: val})}
                        />
                        }
                        <SelectField
                            floatingLabelText="Parent Consent Type"
                            value={this.state.consent}
                            onChange={this.handleChangeConsent}
                        >
                            <MenuItem value={"None"} primaryText="None"/>
                            <MenuItem value={"Fax"} primaryText="Fax"/>
                            <MenuItem value={"Email"} primaryText="Email"/>
                            <MenuItem value={"Letter"} primaryText="Letter"/>
                        </SelectField>
                        <TextField
                            hintText="Address for correspondence during leave"
                            multiLine={true}
                            rows={2}
                            rowsMax={4}
                            value={this.state.corrAdress}
                            onChange={(e, val) => this.setState({corrAdress: val})}
                        />
                        <TextField
                            floatingLabelText="Contact No. during leave"
                            value={this.state.corrPhone}
                            onChange={(e, val) => this.setState({corrPhone: val})}
                        /><br/>
                        {this.state.missingFields?<p style={styles.errorMessage}>All the fields are compulsory</p>:null}
                        <div className={s.applyButton}>
                            <RaisedButton 
                                label="Apply"
                                primary={true} 
                                onClick={(e) => 
                                    {
                                        this.setState({missingFields: false})
                                        if (this.state.reason === "Other") {
                                            this.state.reason = this.state.other;
                                        }
                                        if(this.state.dateEnd&&this.state.dateStart&&this.state.timeEnd&&this.state.timeStart&&this.state.corrAdress&&this.state.corrPhone&&this.state.reason&&this.state.consent){
                                            console.log('all set')
                                            const dateTimeStart = (this.state.dateStart.toISOString().substr(0,10)+this.state.timeStart.toISOString().substr(-14)).substr(0, 19);
                                            const dateTimeEnd = (this.state.dateEnd.toISOString().substr(0,10)+this.state.timeEnd.toISOString().substr(-14)).substr(0, 19);
                                            console.log(dateTimeStart)
                                            console.log(dateTimeEnd)
                                            applyLeave({variables: {dateTimeStart: dateTimeStart, dateTimeEnd: dateTimeEnd, consent: this.state.consent, reason: this.state.reason, corrPhone: this.state.corrPhone, corrAdress: this.state.corrAdress}});
                                            this.setState({timeStart: null, timeEnd: null, dateStart: null, dateEnd: null, dateTimeStart: null, dateTimeEnd: null, reason: "None", consent: "None", corrAdress: "", corrPhone: "", missingFields: false, other: ""})
                                            //this.setState({dateTimeStart: dateTimeStart, dateTimeEnd: dateTimeEnd});
                                        }
                                        else{
                                            this.setState({missingFields: true});
                                            return false;
                                        }  
                                    }}/>
                        </div>
                    </div>
                </Paper>
                )
                }
                </Mutation>
            </Mobile>

        );
    }
}

export default graphql(applyLeave)(Leave);
