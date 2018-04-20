import React from 'react';
import ExpandableCard from "../../../Components/ExpandableCard";


class DuesCard extends React.Component {

    render() {
        if (this.props.dues != null) {

            return (

                <ExpandableCard title={<p>Your total dues are <b>{this.props.dues}</b></p>}
                />
            );
        }

        else {
            <ExpandableCard title={<p>You don't have any dues</p>}/>
        }
    }
}

export default DuesCard;