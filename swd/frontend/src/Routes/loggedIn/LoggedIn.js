import React from "react";
import {Mobile} from "../../Components/Responsive";
import ExpandableCard from "../../Components/ExpandableCard";

class LoggedIn extends React.Component {

    render() {
        return (
            <Mobile>
                <ExpandableCard title={<p>Your current mess option is <b>A</b> dining hall till <b>30th, September,2017.</b></p> }/>
                <ExpandableCard title={<p>Your total dues are <b>RS. 124</b></p>}
                                text={<p>   Rs. 300 : Waves polo tee<br/>
                                            Rs. 345 : Waves pass<br/>
                                    Rs. 1285 : Medical facilities</p>
                }/>
                <div>
                <ExpandableCard title={<p>Your leave has been granted</p>} text={<p>Leave ID: <b>1234</b><br/>
                    Leave from: <b>21/04/18</b><br/>
                    Leave till: <b>23/01/18</b><br/>
                    Warden approval: <b>Yes</b>
                </p>}/>
                 {/*TODO: ADD info card here from main screen*/}


                </div>
            </Mobile>

        );
    }
}


export default LoggedIn;
