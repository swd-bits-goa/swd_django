import React from "react";
import {Mobile} from "../../Components/Responsive";
import ExpandableCardViewMore from "../../Components/ExpandableCardViewMore/ExpandableCardViewMore";
import ExpandableCard from "../../Components/ExpandableCard";


class LoggedIn extends React.Component {

    render() {
        return (
            <Mobile>
               <ExpandableCardViewMore title={"hello"} text={"hello"} cardText={"Yo"}/>
            </Mobile>

        );
    }
}


export default LoggedIn;
