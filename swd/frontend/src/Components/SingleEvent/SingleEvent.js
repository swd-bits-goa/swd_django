import React from 'react';
import {Card, CardActions, CardHeader, CardMedia, CardTitle, CardText} from 'material-ui/Card';
import FlatButton from 'material-ui/FlatButton';

export default class SingleEvent extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            expanded: false,
        };
    }

    handleExpandChange = (expanded) => {
        this.setState({expanded: expanded});
    };

    handleToggle = (event, toggle) => {
        this.setState({expanded: toggle});
    };

    handleExpand = () => {
        this.setState({expanded: true});
    };

    handleReduce = () => {
        this.setState({expanded: false});
    };

    render() {
        return (
            <Card expanded={this.state.expanded} onExpandChange={this.handleExpandChange}>
                <CardHeader
                    title="Quark - T shirt"
                    subtitle="Quark"
                    actAsExpander={true}
                    showExpandableButton={true}
                />

                <CardMedia
                    expandable={true}
                    // overlay={<CardTitle title="Round Hoodie" subtitle="Rs.450" />}
                >
                    //Here URL for image of tshirt goes. Can make this optional for events without a depicting picture.
                    <img src=""/>
                </CardMedia>

                <CardText expandable={true}>
                  Over Here Text Defining the event goes.<br/>
                    <FlatButton label="S" />
                    <FlatButton label="M"/>
                    <FlatButton label="L"/>
                    <FlatButton label="XL"/>
                    <FlatButton label="XXL"/>
                </CardText>

            </Card>
        );
    }
}