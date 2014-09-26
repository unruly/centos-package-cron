import package_checker
import package_fetcher
import errata_fetcher
import os_version_fetcher
import mockable_execute

pkg_fetcher = package_fetcher.PackageFetcher(package_fetcher.ChangeLogParser(),mockable_execute.MockableExecute())
checker = package_checker.PackageChecker(errata_fetcher.ErrataFetcher(),pkg_fetcher,os_version_fetcher.OsVersionFetcher())

send_email = False
security_advisories = list(filter(lambda x:x.type == errata_fetcher.ErrataType.SecurityAdvisory,checker.findAdvisoriesOnInstalledPackages()))
if len(security_advisories) > 0:
	send_email = True
	
general_updates = pkg_fetcher.get_package_updates()
changelogs = []
if len(general_updates) > 0:
	send_email = True
	changelogs = map(lambda pkg: { 'name': pkg.name, 'changelog': pkg_fetcher.get_package_changelog(pkg.name,pkg.version,pkg.release)},general_updates)
	
if send_email == True:
	email_content = 'The following security advisories exist for installed packages:\n\n'
	for advisory in security_advisories:
		email_content += "Advisory ID: %s Severity: %s Packages: %s\n" % (advisory.advisory_id, advisory.severity, advisory.packages)
	email_content += "\n\n"
	for update in general_updates:
		changelog_entry = next(cl for cl in changelogs if cl['name'] == update.name)
		email_content += "Package %s Changelog %s" % (update.name, changelog_entry)
		
	print "Sending email with contents %s" % (email_content)
