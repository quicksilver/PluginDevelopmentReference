//
//  ___PROJECTNAMEASIDENTIFIER___Source.m
//  ___PROJECTNAME___
//
//  Created by ___FULLUSERNAME___ on ___DATE___.
//

#import "___PROJECTNAMEASIDENTIFIER___Source.h"
#import <QSCore/QSObject.h>

@implementation ___PROJECTNAMEASIDENTIFIER___Source

- (BOOL)indexIsValidFromDate:(NSDate *)indexDate forEntry:(NSDictionary *)theEntry
{
	return NO;
}

- (NSImage *)iconForEntry:(NSDictionary *)dict
{
	return nil;
}

// Return a unique identifier for an object (if you haven't assigned one before)
//- (NSString *)identifierForObject:(id <QSObject>)object
//{
//	return nil;
//}

- (NSArray *) objectsForEntry:(NSDictionary *)theEntry
{
	NSMutableArray *objects=[NSMutableArray arrayWithCapacity:1];
	QSObject *newObject;
	
	newObject=[QSObject objectWithName:@"TestObject"];
	[newObject setObject:@"" forType:___PROJECTNAMEASIDENTIFIER___Type];
	[newObject setPrimaryType:___PROJECTNAMEASIDENTIFIER___Type];
	[objects addObject:newObject];
	
	return objects;
}

// Object Handler Methods

/*
- (void)setQuickIconForObject:(QSObject *)object
{
	[object setIcon:nil]; // An icon that is either already in memory or easy to load
}

- (BOOL)loadIconForObject:(QSObject *)object
{
	return NO;
	id data=[object objectForType:k___PROJECTNAMEASIDENTIFIER___Type];
	[object setIcon:nil];
	return YES;
}
*/
@end
