import PropTypes from "prop-types";
import React from 'react';
import {Card, CardHeader, CardText, FlatButton} from "material-ui";
import s from './ExpandableCardViewMore.css';
import Divider from 'material-ui/Divider';

class ExpandableCardViewMore extends React.Component {

    const { title, text, cardText } = props;
    handleExpand = () => {
        this.setState({expanded: true});
    };
    return(
        <div className={s.container}>
            <Card>
                <CardHeader
                    title={title}
                    subtitle={cardText}
                    actAsExpander={true}
                    />
                <Divider />
                <FlatButton label="View More" fullWidth={true}
                onClick={this.handleExpand}/>


                <CardText expandable={true}>
                    {text}

                </CardText>
            </Card>
        </div>
    );
};

ExpandableCardViewMore.propTypes = {
    title: PropTypes.string.isRequired,
    cardText: PropTypes.string,
    text : PropTypes.string
};

export default ExpandableCardViewMore;