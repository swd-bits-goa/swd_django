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

const styles = {
    customWidth: {
        width: 150,
    },
};

class Leave extends React.Component {

    state = {
        value: "None",
        consent: "None",
        other: "None"
    };

    handleChange = (event, index, value) => this.setState({value});
    handleChangeConsent = (event, index, consent) => this.setState({consent});
    handleOther = (event, index, other) => this.setState({other});

    handleClick() {
        if (this.state.value === "Other") {
            this.state.value = this.state.other;
        }
        //Move this to confirmation Page and generate a Leave ID
    }

    render() {
        return (
            <Mobile>
                <div className={s.container}>
                    <Paper zDepth={2}>
                        <div className={s.container2}>
                            <h3>Apply For Leave:</h3>
                            <DatePicker hintText="Departure Date" container="inline"/>
                            <TimePicker
                                hintText="Departure Time"
                                autoOk={true}
                            />
                            <DatePicker hintText="Arrival Date" container="inline"/>
                            <TimePicker
                                hintText="Arrival Time"
                                autoOk={true}
                            />
                            <SelectField
                                floatingLabelText="Reason"
                                value={this.state.value}
                                onChange={this.handleChange}
                            >
                                <MenuItem value={"None"} primaryText="None"/>
                                <MenuItem value={"SisWed"} primaryText="Sister's Wedding"/>
                                <MenuItem value={"BroWed"} primaryText="Brother's Wedding"/>
                                <MenuItem value={"FamilyFunction"} primaryText="Family Function"/>
                                <MenuItem value={"Exam"} primaryText="Examination"/>
                                <MenuItem value={"ParentGoa"} primaryText="To stay with parents in Goa"/>
                                <MenuItem value={"Festivals"} primaryText="Festivals"/>
                                <MenuItem value={"Other"} primaryText="Other"/>
                            </SelectField>
                            {this.state.value === "Other" &&
                            <TextField
                                floatingLabelText="Please Specify Reason Here"
                                onChange={this.handleOther}
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
                            />
                            <TextField
                                floatingLabelText="Contact No. during leave"
                            /><br/>
                            <div className={s.applyButton}>
                                <RaisedButton label="Apply" primary={true} onClick={this.handleClick}/>
                            </div>
                        </div>
                    </Paper>
                </div>
            </Mobile>

        );
    }
}

export default Leave;
