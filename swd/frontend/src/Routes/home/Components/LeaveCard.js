import React from 'react';
import ExpandableCard from "../../../Components/ExpandableCard";
import {FlatButton} from "material-ui";


class LeaveCard extends React.Component {
    applyLeave = () => {
        this.props.history.push("/aboutSWD");
    };

    render() {
        if (this.props.leaveStatus != null) {
            return (
                <ExpandableCard title={<p>Your leave has been {this.props.leaveStatus}</p>}
                                text={<p>Leave ID: <b>{this.props.leaveId}</b><br/>
                                    Leave from: <b>{this.props.leaveFrom}</b><br/>
                                    Leave till: <b>{this.props.leaveTill}</b><br/>
                                    Warden approval: <b>{this.props.wardenApproval}</b><br/><br/>
                                    <FlatButton label="Apply For Leave" onClick={this.applyLeave} fullWidth={true}/>
                                </p>}/>
            );
        }
        else {
            return (
                <ExpandableCard title={<p>You don't have any Leave. Expand to apply for leave</p>}
                                text={<FlatButton label="Apply For Leave" onClick={this.applyLeave}
                                                  fullWidth={true}/>}/>
            )
        }
    }
}

export default LeaveCard;
